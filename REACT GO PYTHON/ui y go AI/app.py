from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnablePassthrough
import logging

app = FastAPI()

class GenerateRequest(BaseModel):
    chat_history: list
    question: str

llm = Ollama(model="llama3.1")

# Define the LangChain setup
loader = WebBaseLoader(web_path="https://blog.langchain.dev/langgraph/")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
all_splits = text_splitter.split_documents(docs)

embeddings = OllamaEmbeddings(model="nomic-embed-text")
vectorstore = Chroma.from_documents(documents=all_splits, embedding=embeddings)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

contextualize_q_system_prompt = """Given a chat history and the latest user question 
which might reference context in the chat history, formulate a standalone question 
which can be understood without the chat history. Do NOT answer the question, 
just reformulate it if needed and otherwise return it as is."""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

qa_system_prompt = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you dont know the answer, just say that you don't know. 
Use three sentences maximum and keep the answer concise.

{context} """

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ]
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def contextualized_question(input: dict):
    if input.get("chat_history"):
        return contextualize_q_chain.invoke(input)
    else:
        return input["question"]

rag_chain = (
    RunnablePassthrough.assign(
        context=contextualized_question | retriever | format_docs
    )
    | qa_prompt
    | llm
)

@app.post("/generate")
async def generate_response(request: GenerateRequest):
    try:
        logging.info(f"Received request: {request}")
        # Use the LangChain setup to process the request
        ai_msg = rag_chain.invoke({
            "question": request.question,
            "chat_history": [{"role": "user", "content": msg["content"]} for msg in request.chat_history]
        })
        logging.info(f"Generated response: {ai_msg}")
        return {"response": ai_msg}
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
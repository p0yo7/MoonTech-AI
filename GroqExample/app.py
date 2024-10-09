from groq import Groq
import streamlit as st

client = Groq(api_key="whatsapp xd")

def get_ai_response(messages):
    # Define el mensaje del sistema
    system_message = {
        "role": "system",
        "content": """Quiero que actúes como un experto en preventas de software. 
    Tu tarea es guiarme en la creación y gestión de propuestas técnicas y comerciales para clientes. 
    Esto incluye definir estándares de la industria, desarrollar historias de usuario, identificar 
    y clasificar los requisitos funcionales y no funcionales, estimar costos detallados, y calcular tiempos y recursos necesarios.
    Además, debes ayudarme a identificar las dependencias entre tareas, prever los riesgos potenciales y proponer estrategias para mitigarlos. 
    También debes considerar diferentes modelos de contratación y metodologías de entrega como SCRUM y Agile, RAD 
    destacando los factores clave de éxito para cada una. Proporciona ejemplos claros y sugerencias prácticas basadas en proyectos 
    previos y buenas prácticas de la industria.
    Finalmente, orienta sobre cómo estructurar la propuesta final, qué documentos incluir,
    y cómo comunicarla de manera efectiva al cliente, asegurando que cubra todos los aspectos 
    relevantes como el alcance, cronograma, costos, y entregables esperados. En caso de necesitar mucho texto, decir al usuario que escriba continua, para que puedas dar mas información de lo mismo, o continuar. IMPORTANTE, SOLO USA 1024 TOKENS POR RESPUESTA.
    """
    }
    
    # Inserta el mensaje del sistema al inicio de la lista de mensajes
    messages.insert(0, system_message)
    
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=messages,
        temperature=0.1,
        max_tokens=1024,
        stream=True,
    )
    
    response = "".join(chunk.choices[0].delta.content or "" for chunk in completion)
    return response

def chat():
    st.title("Chat con llama3.1 con Groq")
    st.write("Bienvenido al chat de llama3.1 con Groq, escribe exit para terminar la conversación.")
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    def submit():
        user_input = st.session_state.user_input
        if user_input.lower() == "exit":
            st.write("Gracias por chatear! Adios.")
            st.stop()

        st.session_state["messages"].append({"role": "user", "content": user_input})

        with st.spinner("Obteniendo respuesta..."):
            ai_response = get_ai_response(st.session_state["messages"])
            st.session_state["messages"].append({"role": "assistant", "content": ai_response})

        st.session_state.user_input = ""

    for message in st.session_state["messages"]:
        role = "Tu" if message["role"] == "user" else "Bot"
        st.write(f"**{role}**: {message['content']}")

    with st.form(key="chat_form", clear_on_submit=True):
        st.text_input("Tu: ", key="user_input")
        submit_button = st.form_submit_button(label="Enviar", on_click=submit)

if __name__ == "__main__":
    chat()
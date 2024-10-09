import React, { useState } from 'react';

const OllamaChat = () => {
    const [prompt, setPrompt] = useState('');
    const [response, setResponse] = useState('');
    const [isTyping, setIsTyping] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const res = await fetch('http://localhost:8080/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: 'llama3.1',
                    stream: false,
                    prompt: prompt,
                }),
            });

            const data = await res.json();
            typeResponse(data.response); // Llama a la función para escribir la respuesta lentamente
        } catch (error) {
            console.error('Error:', error);
            setResponse('Error fetching response.');
        }
    };

    // Función para simular la escritura lenta
    const typeResponse = (text) => {
        setIsTyping(true);
        setResponse(''); // Resetea la respuesta antes de iniciar la escritura
        let index = 0;

        const interval = setInterval(() => {
            if (index < text.length) {
                setResponse((prev) => prev + text.charAt(index)); // Añade un carácter a la vez
                index++;
            } else {
                clearInterval(interval);
                setIsTyping(false);
            }
        }, 50); // Ajusta el tiempo para la velocidad de escritura
    };

    return (
        <div>
            <h1>Ollama Chat</h1>
            <form onSubmit={handleSubmit}>
                <label>
                    Prompt:
                    <input
                        type="text"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        required
                    />
                </label>
                <button type="submit">Send</button>
            </form>
            {response && (
                <div>
                    <h2>Response:</h2>
                    <p>{response}</p>
                </div>
            )}
        </div>
    );
};

export default OllamaChat;

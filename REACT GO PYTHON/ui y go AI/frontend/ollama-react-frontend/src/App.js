import React, { useState } from 'react';
import axios from 'axios';
import {
    Container,
    TextField,
    Button,
    Typography,
    Box,
    Paper,
} from '@mui/material';

function App() {
    const [prompt, setPrompt] = useState('');
    const [history, setHistory] = useState([]);
    const [response, setResponse] = useState('');
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        const newHistory = [
            ...history,
            { role: 'user', content: prompt },
            { role: 'assistant', content: '' }
        ];
        setHistory(newHistory);

        try {
            const requestData = {
                chat_history: newHistory,
                question: prompt,
            };
            console.log("Request data:", requestData); // Verifica los datos que se están enviando

            const res = await axios.post('http://localhost:8081/api/generate', requestData);
            console.log("Response from backend:", res.data); // Verifica la respuesta del backend
            setResponse(res.data.response); // Muestra la respuesta actual
            const updatedHistory = newHistory.map((item, index) =>
                index === newHistory.length - 1 ? { ...item, content: res.data.response } : item
            );
            setHistory(updatedHistory); // Actualiza el historial con la respuesta
        } catch (error) {
            console.error("Error:", error);
        }
    };

    return (
        <Container maxWidth="sm" sx={{ mt: 4 }}>
            <Typography variant="h4" gutterBottom>
                Generador de Prompts
            </Typography>
            <Paper elevation={3} sx={{ padding: 2 }}>
                <form onSubmit={handleSubmit}>
                    <TextField
                        label="Escribe tu prompt aquí"
                        variant="outlined"
                        fullWidth
                        multiline
                        rows={4}
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        sx={{ mb: 2 }}
                    />
                    <Box textAlign="center">
                        <Button type="submit" variant="contained" color="primary">
                            Enviar
                        </Button>
                    </Box>
                </form>
            </Paper>
            <Typography variant="h5" sx={{ mt: 4 }}>
                Respuestas Históricas:
            </Typography>
            <Paper elevation={1} sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: 1 }}>
                {history.map((item, index) => (
                    <Typography key={index} variant="body2">
                        <strong>{item.role === 'user' ? 'User' : 'Bot'}:</strong> {item.content}
                    </Typography>
                ))}
            </Paper>
            <Typography variant="h5" sx={{ mt: 4 }}>
                Respuesta Actual:
            </Typography>
            <Typography variant="body1" sx={{ bgcolor: '#f5f5f5', p: 2, borderRadius: 1 }}>
                {response}
            </Typography>
        </Container>
    );
}

export default App;
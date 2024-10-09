package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"

    "github.com/gin-contrib/cors"
    "github.com/gin-gonic/gin"
)

type GenerateRequest struct {
    ChatHistory []map[string]string `json:"chat_history"`
    Question    string              `json:"question"`
}

type GenerateResponse struct {
    Response string `json:"response"`
}

func main() {
    r := gin.Default()

    // Habilitar CORS
    r.Use(cors.Default())

    r.POST("/api/generate", func(c *gin.Context) {
        var request GenerateRequest
        if err := c.ShouldBindJSON(&request); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            return
        }

        // Configura la solicitud al servicio Python
        jsonData, _ := json.Marshal(request)

        resp, err := http.Post("http://localhost:8000/generate", "application/json", bytes.NewBuffer(jsonData))
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Error contacting the Python service"})
            return
        }
        defer resp.Body.Close()

        var response GenerateResponse
        if err := json.NewDecoder(resp.Body).Decode(&response); err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": "Error decoding response"})
            return
        }

        // Imprimir la respuesta para depuración
        fmt.Println("Response from Python service:", response)

        c.JSON(http.StatusOK, response)
    })

    r.Run(":8081") // Corre el servidor en el puerto 8081
}
import express from "express";
import { WebSocketServer } from "ws";
import http from "http";
import fetch from "node-fetch"; // If Node >=18, native fetch is available

const app = express();
const server = http.createServer(app);

// Serve static files (our frontend in "public" folder)
app.use(express.static("public"));

// Setup WebSocket
const wss = new WebSocketServer({ server });

wss.on("connection", (ws) => {
  console.log("Client connected");

  ws.on("message", async (message) => {
    const userMessage = message.toString();
    console.log("Received:", userMessage);

    // Broadcast user message to everyone
    wss.clients.forEach((client) => {
      if (client.readyState === ws.OPEN) {
        client.send(JSON.stringify({ sender: "user", text: userMessage }));
      }
    });

    // Call Flask backend for AI response
    try {
      const aiResponse = await getAIResponse(userMessage);
      console.log(" aiResponse ", aiResponse)

      // Send AI response only to the sender
      ws.send(JSON.stringify({ sender: "ai", text: aiResponse }));
    } catch (err) {
      console.error("Error getting AI response:", err);
      ws.send(JSON.stringify({ sender: "ai", text: "⚠️ AI backend error" }));
    }
  });

  ws.on("close", () => {
    console.log("Client disconnected");
  });
});

// Helper: Fetch AI reply from Flask backend
async function getAIResponse(message) {
  const res = await fetch("http://localhost:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const data = await res.json();
  return data.reply || "🤖 (no response)";
}

// Start server
const PORT = 3000;
server.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});

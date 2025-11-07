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
    const messageStr = message.toString();

    // Parse message - could be plain text or JSON
    let userMessage;
    let selectedFiles = null;

    try {
      const parsed = JSON.parse(messageStr);
      userMessage = parsed.message;
      selectedFiles = parsed.selectedFiles;
    } catch {
      // If not JSON, treat as plain text (backward compatibility)
      userMessage = messageStr;
    }

    console.log("Received:", userMessage);
    if (selectedFiles) {
      console.log("Selected files:", selectedFiles);
    }

    // Broadcast user message to everyone
    wss.clients.forEach((client) => {
      if (client.readyState === ws.OPEN) {
        client.send(JSON.stringify({ sender: "user", text: userMessage }));
      }
    });

    // Call Flask backend for AI response
    try {
      const aiData = await getAIResponse(userMessage, selectedFiles);
      console.log(" aiResponse ", aiData);

      // Send AI response only to the sender with RAG info
      ws.send(
        JSON.stringify({
          sender: "ai",
          text: aiData.reply,
          usedRag: aiData.used_rag || false,
          sources: aiData.sources || []
        })
      );
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
async function getAIResponse(message, selectedFiles = null) {
  const requestBody = { message };

  // Add selected files to request if provided
  if (selectedFiles && selectedFiles.length > 0) {
    requestBody.selected_files = selectedFiles;
  }

  const res = await fetch("http://localhost:5001/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestBody),
  });

  const data = await res.json();
  return {
    reply: data.reply || "🤖 (no response)",
    used_rag: data.used_rag || false,
    retrieved_chunks: data.retrieved_chunks || 0,
    sources: data.sources || []
  };
}

// Start server
const PORT = 3000;
server.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});

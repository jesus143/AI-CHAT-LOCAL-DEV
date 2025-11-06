# 🤖 AI Chat Application

## Overview
This project has evolved into a full **RAG (Retrieval-Augmented Generation)** application! 

### Features:
- ✅ Real-time AI chat interface
- ✅ **File upload (PDF, DOCX, TXT)**
- ✅ **Question-answering based on uploaded documents**
- ✅ Vector similarity search with ChromaDB
- ✅ Semantic embeddings using Sentence Transformers
- ✅ Local AI with Ollama (phi4-mini:3.8b)

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Ollama installed with phi4-mini:3.8b model

### 1. Install Ollama Model
```bash
ollama pull phi4-mini:3.8b
```

### 2. Setup Python Backend
```bash
cd AI-CHAT-LOCAL-DEV/python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
🟢 Flask server running on http://127.0.0.1:5000

### 3. Setup Node.js Server
```bash
cd AI-CHAT-LOCAL-DEV
npm install
npm run dev
```
🟢 WebSocket server running on http://localhost:3000

### 4. Open Browser
Visit: **http://localhost:3000**

## 📚 Full Documentation

For complete setup instructions, architecture details, and troubleshooting, see:
**[RAG_SETUP.md](./RAG_SETUP.md)**

## Test the RAG System

1. Upload the included `sample_document.txt` file
2. Ask questions like:
   - "What does Acme Technology Solutions do?"
   - "Where is the company located?"
   - "What are their office hours?"
   - "How can I contact support?"

## Tech Stack

**Frontend**: HTML/CSS/JavaScript (WebSocket)  
**Backend**: Flask (Python) + Node.js  
**AI/ML**: Ollama (phi4-mini:3.8b), Sentence Transformers  
**Vector DB**: ChromaDB  
**Document Processing**: PyPDF2, python-docx

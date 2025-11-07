# 🚀 RAG AI Chat Application - Setup Guide

## Overview
This is a **Retrieval-Augmented Generation (RAG)** application that allows you to:
1. Upload documents (PDF, DOCX, TXT)
2. Ask questions about those documents
3. Get AI-powered answers based on the document content

## Architecture

```
┌─────────────┐      WebSocket      ┌──────────────┐
│   Frontend  │ ◄─────────────────► │   Node.js    │
│   (HTML)    │                     │   Server     │
└─────────────┘                     └──────────────┘
       │                                    │
       │ HTTP (File Upload)          HTTP (Chat)
       │                                    │
       ▼                                    ▼
┌─────────────────────────────────────────────────┐
│              Flask Backend (Python)              │
│  - File processing                               │
│  - Text extraction & chunking                    │
│  - Vector embeddings (Sentence Transformers)     │
│  - Similarity search (ChromaDB)                  │
│  - AI responses (Ollama + phi4-mini)            │
└─────────────────────────────────────────────────┘
```

## Tech Stack

### Frontend
- HTML/CSS/JavaScript
- WebSocket for real-time chat
- Drag-and-drop file upload

### Backend
- **Node.js** - WebSocket server for real-time communication
- **Flask** - Python REST API
- **ChromaDB** - Vector database for embeddings
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)
- **Ollama** - Local LLM runtime
- **phi4-mini:3.8b** - Language model

### Document Processing
- **PyPDF2** - PDF text extraction
- **python-docx** - Word document processing
- Plain text file support

## Installation & Setup

### Prerequisites
1. **Python 3.8+**
2. **Node.js 16+**
3. **Ollama** - Install from https://ollama.ai

### Step 1: Install Ollama Model
```bash
# Install Ollama if you haven't already
# Visit: https://ollama.ai

# Pull the phi4-mini model
ollama pull phi4-mini:3.8b
```

### Step 2: Setup Python Environment
```bash
# Navigate to python directory
cd AI-CHAT-LOCAL-DEV/python

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note**: First time installation may take several minutes as it downloads the sentence-transformers model (~80MB).

### Step 3: Setup Node.js
```bash
# Navigate to project root
cd AI-CHAT-LOCAL-DEV

# Install dependencies
npm install
```

## Running the Application

You need to run **TWO** servers:

### Terminal 1: Flask Backend
```bash
cd AI-CHAT-LOCAL-DEV/python
source venv/bin/activate
python app.py
```

Expected output:
```
 * Running on http://127.0.0.1:5000
```

### Terminal 2: Node.js Server
```bash
cd AI-CHAT-LOCAL-DEV
npm run dev
```

Expected output:
```
🚀 Server running at http://localhost:3000
```

### Access the Application
Open your browser and go to:
```
http://localhost:3000
```

## How to Use

### 1. Upload Documents
- Click or drag-and-drop files into the upload area (left sidebar)
- Supported formats: PDF, DOCX, TXT
- Maximum file size: 16MB
- Files are automatically processed and indexed

### 2. Ask Questions
- Type your question in the chat input
- The AI will search for relevant context from your uploaded documents
- Answers will be based on the document content
- Messages marked with "✓ Answer based on your documents" used RAG

### 3. Manage Documents
- View statistics in the sidebar (total chunks, status)
- Click "Clear All Documents" to remove all uploaded files from the index

## Features

### ✨ Core Features
- **Document Upload**: Support for PDF, DOCX, and TXT files
- **Smart Chunking**: Documents are split into ~500 character chunks with 50 character overlap
- **Vector Search**: Uses semantic similarity to find relevant content
- **Context-Aware Responses**: AI answers based on retrieved document chunks
- **Real-time Chat**: WebSocket-based instant messaging
- **Visual Feedback**: Shows when RAG was used for answers

### 🎨 UI Features
- Modern, clean interface
- Drag-and-drop file upload
- Live statistics dashboard
- Toast notifications
- Loading indicators
- Code syntax highlighting

## API Endpoints

### Flask Backend (Port 5000)

#### POST `/upload`
Upload and process a document
```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@document.pdf"
```

#### POST `/chat`
Send a chat message
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is this document about?"}'
```

#### GET `/stats`
Get vector store statistics
```bash
curl http://localhost:5000/stats
```

#### POST `/clear`
Clear all documents from vector store
```bash
curl -X POST http://localhost:5000/clear
```

## Project Structure

```
AI-CHAT-LOCAL-DEV/
├── python/
│   ├── app.py                 # Flask backend
│   ├── document_processor.py  # File processing & chunking
│   ├── vector_store.py        # ChromaDB vector operations
│   ├── requirements.txt       # Python dependencies
│   ├── uploads/              # Uploaded files (auto-created)
│   └── chroma_db/            # Vector database (auto-created)
├── public/
│   └── index.html            # Frontend interface
├── server.js                 # Node.js WebSocket server
├── package.json              # Node.js dependencies
└── RAG_SETUP.md             # This file
```

## Troubleshooting

### Issue: "Ollama not found"
**Solution**: Install Ollama from https://ollama.ai and run `ollama pull phi4-mini:3.8b`

### Issue: "Module not found" errors
**Solution**: Make sure you activated the virtual environment and installed requirements:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: File upload fails
**Solution**: 
- Check that Flask server is running
- Verify file format is supported (PDF, DOCX, TXT)
- Check file size is under 16MB

### Issue: ChromaDB errors
**Solution**: Try clearing the database:
```bash
rm -rf python/chroma_db
# Then restart Flask server
```

### Issue: WebSocket connection fails
**Solution**: 
- Ensure Node.js server is running on port 3000
- Check that no other service is using port 3000

## Advanced Configuration

### Change Chunk Size
Edit `python/app.py`, line ~165:
```python
chunks = doc_processor.chunk_text(text, chunk_size=500, overlap=50)
```

### Change Number of Retrieved Chunks
Edit `python/app.py`, line ~55:
```python
retrieved_chunks = vector_store.search(user_message, n_results=3)
```

### Change Embedding Model
Edit `python/vector_store.py`, line ~27:
```python
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
```

Popular alternatives:
- `all-mpnet-base-v2` (better quality, slower)
- `paraphrase-MiniLM-L3-v2` (faster, smaller)

### Change LLM Model
Edit `python/app.py`, line ~85:
```python
["ollama", "run", "phi4-mini:3.8b", prompt],
```

Other Ollama models:
- `llama2`
- `mistral`
- `codellama`

## Performance Notes

- First-time setup downloads ~80MB model for embeddings
- Each document upload involves:
  - Text extraction: Fast (< 1 second for most files)
  - Embedding generation: ~0.1-0.5 seconds per chunk
  - Vector storage: Near instant
- Query time: ~0.5-1 second (includes retrieval + LLM generation)

## Security Considerations

⚠️ **This is a development setup. For production:**
- Add authentication
- Implement file validation
- Use HTTPS
- Add rate limiting
- Sanitize file uploads
- Use environment variables for configuration

## License

This is a practice project for learning RAG applications.

## Support

For issues or questions about:
- **Ollama**: https://github.com/ollama/ollama
- **ChromaDB**: https://docs.trychroma.com/
- **Sentence Transformers**: https://www.sbert.net/

---

**Happy Learning! 🎉**


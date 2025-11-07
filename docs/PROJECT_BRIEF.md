# RAG AI Chat Application - Brief Overview

## What It Is
A **Retrieval-Augmented Generation (RAG)** application that allows users to upload documents and ask intelligent questions about their content using AI.

## Core Functionality
1. **Upload documents** (PDF, DOCX, TXT)
2. **Automatic processing** - Text extraction, chunking, and vectorization
3. **Selective file querying** - Choose which documents to search for each question
4. **Ask questions** - AI retrieves relevant context and generates accurate answers
5. **Real-time chat** - WebSocket-based interface with instant responses

## Technology Stack

**Backend**
- Python (Flask) - REST API and document processing
- Node.js + WebSocket - Real-time communication
- FAISS - Vector similarity search
- Sentence Transformers - Text embeddings
- Ollama (phi4-mini) - Local AI model

**Frontend**
- HTML/CSS/JavaScript
- WebSocket API
- Drag-and-drop file upload

## Key Features
✅ Multi-format document support (PDF, DOCX, TXT)  
✅ Semantic search using vector embeddings  
✅ **Selective file search** - Choose which documents to query  
✅ Context-aware AI responses with source attribution  
✅ Real-time chat interface  
✅ Document management dashboard with checkboxes  
✅ Local AI (no API keys required)  

## Technical Highlights

### Problem Solved #1: Multiprocessing Issues
Debugged and fixed semaphore leak issues caused by sentence-transformers' parallel processing conflicting with Flask's debug mode. Implemented environment-level fixes and model initialization strategies.

### Problem Solved #2: Library Compatibility
Migrated from ChromaDB to FAISS to resolve Python 3.13 and macOS 12.x compatibility issues, reducing dependencies while maintaining performance.

### Feature Added: Selective File Querying
Implemented document filtering UI with checkboxes allowing users to select which files to search. Backend efficiently filters vector search results by filename, enabling focused queries on specific documents.

## Skills Demonstrated
- Full-stack development (Python, JavaScript, Node.js)
- AI/ML integration (embeddings, vector search, LLMs)
- System architecture and API design
- Problem-solving and debugging
- Technical documentation

## Performance
- Query response: ~0.5-1 second
- Supports documents up to 16MB
- Efficient chunking with 500-char chunks and 50-char overlap
- Memory footprint: ~500MB

## Documentation Provided
- Complete setup guide
- API documentation
- Architecture diagrams
- Troubleshooting guides
- Technical decision documentation

## Project Status
✅ **Fully functional** and ready for demonstration  
📅 **Completed**: November 2025  
🔧 **Code**: Clean, modular, well-documented  

---

## Demo Available
I can provide:
- Live walkthrough of the application
- Code repository access
- Technical deep-dive on any component
- Discussion of design decisions

---

**Quick Stats**: 3 Python modules, 5 REST endpoints, WebSocket server, full RAG pipeline with file filtering, comprehensive documentation

*Built to demonstrate practical AI/ML engineering, full-stack capabilities, and production-ready coding practices.*


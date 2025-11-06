import os
# Set environment variables before any other imports to prevent multiprocessing issues
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['OMP_NUM_THREADS'] = '1'

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import subprocess
import sys
import sqlite3
import re

from document_processor import DocumentProcessor
from vector_store import VectorStore

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Performance Configuration
N_RESULTS = 2  # Number of chunks to retrieve (2 is faster, 3 is more context)
CHUNK_SIZE = 500  # Chunk size in characters (smaller = faster, larger = more context)
CHUNK_OVERLAP = 50  # Overlap between chunks

# Global conversation history
conversation_history = []
MAX_HISTORY = 10  # keep only last 10 exchanges
DB_PATH = "test.db"  # SQLite file

# Initialize RAG components
doc_processor = DocumentProcessor(UPLOAD_FOLDER)
vector_store = VectorStore()

def allowed_file(filename):
    """Check if file has an allowed extension"""
    if '.' not in filename:
        return False
    try:
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in ALLOWED_EXTENSIONS
    except IndexError:
        return False


@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history

    data = request.get_json()
    user_message = data.get("message", "")
    use_rag = data.get("use_rag", True)  # Use RAG by default if documents are available
    selected_files = data.get("selected_files", None)  # Optional list of filenames to filter

    if not user_message:
        return jsonify({"error": "Please provide a message"}), 400

    logger("User: " + user_message)
    if selected_files:
        logger(f"Selected files: {selected_files}")
    
    # Check if we should use RAG
    context = ""
    retrieved_chunks = []
    if use_rag:
        stats = vector_store.get_collection_stats()
        if stats['total_chunks'] > 0:
            # Retrieve relevant context from vector store
            # Pass selected_files to filter search (None = search all files)
            retrieved_chunks = vector_store.search(user_message, n_results=N_RESULTS, filenames=selected_files)
            if retrieved_chunks:
                context = "\n\nRelevant context from uploaded documents:\n"
                for i, chunk in enumerate(retrieved_chunks, 1):
                    context += f"\n[Context {i}] (from {chunk['filename']}):\n{chunk['text']}\n"
                logger(f"Retrieved {len(retrieved_chunks)} relevant chunks")
    
    # Build message with context if available
    message_with_context = user_message
    if context:
        message_with_context = f"{context}\n\nQ: {user_message}\n\nAnswer concisely and short as possible based on context above. If unsure, say 'Not sure based on provided info.'"
    else:
        message_with_context = f"{user_message}\n\nAnswer as concisely as possible and short as possible."
    
    conversation_history.append({
        "role": "user",
        "content": message_with_context
    })

    conversation_history[:] = conversation_history[-MAX_HISTORY:]  # trim history

    # Build prompt
    prompt = ""
    for entry in conversation_history:
        prompt += f"{entry['role'].capitalize()}: {entry['content']}\n"
    prompt += "AI:"

    # Call Ollama
    try:
        result = subprocess.run(
            ["ollama", "run", "phi4-mini:3.8b", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        ai_response = result.stdout.strip()
    except Exception as e:
        ai_response = f"Error generating response: {e}"

    logger("AI: " + ai_response)

    # Try to execute SQL if present
    sql_result = None
    if contains_sql(ai_response):
        sql_result = execute_sql(ai_response)

    conversation_history.append({"role": "ai", "content": ai_response})

    return jsonify({
        "reply": ai_response,
        "sql_result": sql_result,
        "history": conversation_history,
        "retrieved_chunks": len(retrieved_chunks),
        "used_rag": len(retrieved_chunks) > 0
    })


def contains_sql(text):
    """Check if text contains SQL command"""
    sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP"]
    return any(keyword in text.upper() for keyword in sql_keywords)


def execute_sql(query):
    """Run SQL query on SQLite database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(query)

        if query.strip().upper().startswith("SELECT"):
            rows = cur.fetchall()
            conn.close()
            return {"rows": rows}
        else:
            conn.commit()
            conn.close()
            return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}


def logger(message):
    print(f"INFO {message}", file=sys.stderr)


@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload and process for RAG"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            
            # Ensure filename still has extension after secure_filename
            if not filename or '.' not in filename:
                return jsonify({"error": "Invalid filename after sanitization"}), 400
            
            # Save file
            filepath = doc_processor.save_file(file, filename)
            logger(f"File saved: {filepath}")
            
            # Extract text
            text = doc_processor.extract_text(filepath)
            logger(f"Extracted {len(text)} characters from {filename}")
            
            # Chunk text
            chunks = doc_processor.chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
            logger(f"Created {len(chunks)} chunks")
            
            # Add to vector store
            num_added = vector_store.add_documents(chunks, filename)
            logger(f"Added {num_added} chunks to vector store")
            
            return jsonify({
                "message": "File uploaded and processed successfully",
                "filename": filename,
                "text_length": len(text),
                "num_chunks": num_added,
                "stats": vector_store.get_collection_stats()
            })
        
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            logger(f"Error processing file: {e}")
            logger(f"Traceback: {error_detail}")
            return jsonify({"error": f"Error processing file: {str(e)}"}), 500
    
    return jsonify({"error": "File type not allowed. Please upload txt, pdf, or docx files."}), 400


@app.route("/stats", methods=["GET"])
def get_stats():
    """Get vector store statistics"""
    stats = vector_store.get_collection_stats()
    return jsonify(stats)


@app.route("/files", methods=["GET"])
def list_files():
    """List all uploaded files with metadata"""
    files = vector_store.get_uploaded_files()
    return jsonify({"files": files})


@app.route("/clear", methods=["POST"])
def clear_documents():
    """Clear all documents from vector store"""
    try:
        vector_store.clear_collection()
        return jsonify({"message": "All documents cleared successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Start with a test table if not exists
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER)")
    conn.commit()
    conn.close()

    app.run(debug=True, host="0.0.0.0", port=5001)

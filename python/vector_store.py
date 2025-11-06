"""
Vector store for RAG application using FAISS
Handles embedding generation and similarity search
"""
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import pickle
import os

# Prevent multiprocessing issues with tokenizers and sentence transformers
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['OMP_NUM_THREADS'] = '1'


class VectorStore:
    def __init__(self, persist_directory: str = "./faiss_db", collection_name: str = "documents"):
        """Initialize FAISS and embedding model"""
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        os.makedirs(persist_directory, exist_ok=True)
        
        self.index_path = os.path.join(persist_directory, f"{collection_name}.index")
        self.metadata_path = os.path.join(persist_directory, f"{collection_name}_metadata.pkl")
        
        # Load embedding model (using a lightweight model)
        # Set device to 'cpu' explicitly and disable multiprocessing
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        self.embedding_model.encode("warmup", show_progress_bar=False)  # Warmup to initialize model
        self.dimension = 384  # all-MiniLM-L6-v2 embedding dimension
        
        # Initialize or load FAISS index
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            # Create a new FAISS index (L2 distance)
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
        
    def add_documents(self, chunks: List[Dict], filename: str) -> int:
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of text chunks with metadata
            filename: Name of the source file
        
        Returns:
            Number of chunks added
        """
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        
        # Add embeddings to FAISS index
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Store metadata
        for i, chunk in enumerate(chunks):
            self.metadata.append({
                "text": texts[i],
                "filename": filename,
                "chunk_id": chunk["chunk_id"],
                "length": chunk["length"]
            })
        
        # Save index and metadata
        self._save()
        
        return len(chunks)
    
    def search(self, query: str, n_results: int = 3, filenames: List[str] = None) -> List[Dict]:
        """
        Search for relevant document chunks
        
        Args:
            query: The search query
            n_results: Number of results to return
            filenames: Optional list of filenames to filter by (None = all files)
        
        Returns:
            List of relevant chunks with metadata
        """
        if self.index.ntotal == 0:
            return []
        
        # Generate embedding for query
        query_embedding = self.embedding_model.encode([query], show_progress_bar=False, convert_to_numpy=True)
        
        # If filtering by filenames, we need to search more and then filter
        search_limit = self.index.ntotal if filenames else n_results
        search_limit = min(search_limit, self.index.ntotal)
        
        # Search in FAISS index
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'), 
            search_limit
        )
        
        # Format and filter results
        formatted_results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["distance"] = float(distances[0][i])
                
                # Apply filename filter if provided
                if filenames is None or result["filename"] in filenames:
                    formatted_results.append(result)
                    
                    # Stop if we have enough results
                    if len(formatted_results) >= n_results:
                        break
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the current collection"""
        return {
            "total_chunks": self.index.ntotal,
            "collection_name": self.collection_name
        }
    
    def get_uploaded_files(self) -> List[Dict]:
        """Get list of all uploaded files with chunk counts"""
        files_map = {}
        
        for chunk in self.metadata:
            filename = chunk["filename"]
            if filename not in files_map:
                files_map[filename] = {
                    "filename": filename,
                    "chunk_count": 0
                }
            files_map[filename]["chunk_count"] += 1
        
        return list(files_map.values())
    
    def clear_collection(self):
        """Clear all documents from the collection"""
        # Create a new empty index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        
        # Save empty index
        self._save()
    
    def _save(self):
        """Save index and metadata to disk"""
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)

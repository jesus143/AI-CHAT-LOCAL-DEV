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
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
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
        embeddings = self.embedding_model.encode(texts)
        
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
    
    def search(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Search for relevant document chunks
        
        Args:
            query: The search query
            n_results: Number of results to return
        
        Returns:
            List of relevant chunks with metadata
        """
        if self.index.ntotal == 0:
            return []
        
        # Generate embedding for query
        query_embedding = self.embedding_model.encode([query])
        
        # Search in FAISS index
        n_results = min(n_results, self.index.ntotal)
        distances, indices = self.index.search(
            np.array(query_embedding).astype('float32'), 
            n_results
        )
        
        # Format results
        formatted_results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result["distance"] = float(distances[0][i])
                formatted_results.append(result)
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the current collection"""
        return {
            "total_chunks": self.index.ntotal,
            "collection_name": self.collection_name
        }
    
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

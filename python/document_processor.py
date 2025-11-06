"""
Document processor for RAG application
Handles file upload, text extraction, and document chunking
"""
import os
from pathlib import Path
import PyPDF2
import docx
from typing import List, Dict


class DocumentProcessor:
    def __init__(self, upload_folder: str = "uploads"):
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
    
    def save_file(self, file, filename: str) -> str:
        """Save uploaded file and return the path"""
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        return filepath
    
    def extract_text(self, filepath: str) -> str:
        """Extract text from different file formats"""
        file_ext = Path(filepath).suffix.lower()
        
        if file_ext == '.pdf':
            return self._extract_from_pdf(filepath)
        elif file_ext == '.docx':
            return self._extract_from_docx(filepath)
        elif file_ext == '.txt':
            return self._extract_from_txt(filepath)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _extract_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if not text.strip():
                raise ValueError("No text could be extracted from PDF. It may be image-based or encrypted.")
            
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_from_docx(self, filepath: str) -> str:
        """Extract text from DOCX file"""
        doc = docx.Document(filepath)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    def _extract_from_txt(self, filepath: str) -> str:
        """Extract text from TXT file"""
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, any]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: The text to chunk
            chunk_size: Number of characters per chunk
            overlap: Number of characters to overlap between chunks
        
        Returns:
            List of dictionaries with chunk text and metadata
        """
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        chunk_id = 0
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1  # +1 for space
            
            if current_length >= chunk_size:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "chunk_id": chunk_id,
                    "length": len(chunk_text)
                })
                
                # Create overlap for next chunk
                overlap_words = int(len(current_chunk) * (overlap / chunk_size))
                current_chunk = current_chunk[-overlap_words:] if overlap_words > 0 else []
                current_length = sum(len(w) + 1 for w in current_chunk)
                chunk_id += 1
        
        # Add remaining text as last chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "chunk_id": chunk_id,
                "length": len(chunk_text)
            })
        
        return chunks


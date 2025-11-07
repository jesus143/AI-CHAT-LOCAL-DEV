# Performance Optimization Guide

## Current Performance
- **Query response time**: ~0.5-1 second
- **Embedding generation**: ~0.1-0.5 seconds
- **LLM generation**: ~0.5-1 second
- **Vector search**: ~0.01 seconds

## 🚀 Quick Wins (Immediate)

### 1. Reduce Number of Retrieved Chunks
**Impact**: 20-30% faster
**Difficulty**: Easy

Change from 3 to 2 chunks in `python/app.py`:
```python
# Line 70
retrieved_chunks = vector_store.search(user_message, n_results=2, filenames=selected_files)
```

### 2. Use Smaller/Faster LLM Model
**Impact**: 40-60% faster
**Difficulty**: Easy

Switch to a faster Ollama model in `python/app.py`:
```bash
# Install faster model
ollama pull phi3.5:mini

# Or even faster
ollama pull tinyllama
```

Then update `python/app.py` line 95:
```python
["ollama", "run", "phi3.5:mini", prompt],
# or
["ollama", "run", "tinyllama", prompt],
```

### 3. Reduce Chunk Size
**Impact**: 10-15% faster
**Difficulty**: Easy

Smaller chunks = less text to process:
```python
# In python/app.py, line 186
chunks = doc_processor.chunk_text(text, chunk_size=300, overlap=30)
```

## 🎯 Medium Impact Optimizations

### 4. Add Query Caching
**Impact**: 80-90% faster for repeated queries
**Difficulty**: Medium

Add simple in-memory cache to avoid re-processing identical queries.

### 5. Use GPU Acceleration
**Impact**: 50-70% faster embeddings
**Difficulty**: Medium (requires CUDA-capable GPU)

If you have an NVIDIA GPU:
```bash
pip uninstall faiss-cpu
pip install faiss-gpu
```

Update `vector_store.py`:
```python
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cuda')
```

### 6. Async/Parallel Processing
**Impact**: 30-40% faster
**Difficulty**: Medium

Process embedding and context building in parallel.

## ⚡ Advanced Optimizations

### 7. Streaming LLM Responses
**Impact**: Perceived 90% faster (starts showing text immediately)
**Difficulty**: Hard

Stream tokens as they're generated instead of waiting for full response.

### 8. Quantized Embedding Model
**Impact**: 40-50% faster embeddings
**Difficulty**: Medium

Use ONNX quantized models for faster inference.

### 9. Pre-compute Common Queries
**Impact**: 95% faster for common questions
**Difficulty**: Medium

Cache embeddings for frequently asked questions.

## 📊 Recommended Implementation Order

1. **Change to 2 chunks** (5 minutes) → 20-30% faster
2. **Use faster LLM model** (10 minutes) → 40-60% faster
3. **Add query caching** (30 minutes) → 80-90% for repeat queries
4. **Reduce chunk size** (5 minutes) → 10-15% faster
5. **GPU acceleration** (if available) → 50-70% faster embeddings

Combined: **70-80% faster overall response time**

## 🛠️ Implementation Priority

### Immediate (< 15 minutes):
- Reduce chunks to 2
- Switch to faster LLM
- Reduce chunk size

### This Week (1-2 hours):
- Add query caching
- Implement async processing

### Optional (if you have GPU):
- Install FAISS-GPU
- Enable CUDA for embeddings

---

**Expected Results After Quick Wins:**
- Current: 0.5-1 second
- After: 0.2-0.4 seconds (60-80% faster!)


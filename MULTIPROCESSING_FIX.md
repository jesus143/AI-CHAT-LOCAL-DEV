# Multiprocessing Issue Fix

## Problem
The Python backend was stopping execution after file uploads with this error:
```
/opt/homebrew/Cellar/python@3.13/3.13.1/Frameworks/Python.framework/Versions/3.13/lib/python3.13/multiprocessing/resource_tracker.py:276: UserWarning: resource_tracker: There appear to be 2 leaked semaphore objects to clean up at shutdown
```

## Root Cause
The `sentence-transformers` library (used for generating embeddings) internally uses:
- **tokenizers** - which uses multiprocessing by default
- **joblib** - which creates process pools
- **OpenMP** - which spawns multiple threads

When combined with Flask's debug mode (which uses a reloader that spawns multiple processes), this created leaked semaphore objects that caused the application to hang or crash.

## Solution Applied

### 1. Environment Variables Set
Added environment variables in multiple locations to disable parallelism:
- `TOKENIZERS_PARALLELISM=false` - Disables parallel tokenization
- `OMP_NUM_THREADS=1` - Limits OpenMP to single thread

### 2. Files Modified

#### `python/app.py`
- Added environment variables at the very top, before any imports
- This ensures variables are set before any multiprocessing libraries load

#### `python/vector_store.py`
- Added environment variables in the module
- Modified `SentenceTransformer` initialization to explicitly use CPU device
- Added warmup call to initialize model properly
- Updated `encode()` calls to use:
  - `show_progress_bar=False` - Disables progress bar (which uses multiprocessing)
  - `convert_to_numpy=True` - Direct numpy conversion without intermediate steps

#### `start-backend.sh`
- Added export statements for environment variables
- Ensures variables are set at the shell level before Python starts

## How to Use

Simply restart your backend using the startup script:
```bash
./start-backend.sh
```

Or if running manually:
```bash
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1
cd python
source venv/bin/activate
python app.py
```

## What to Expect

✅ **Before**: Application would hang/crash after file upload with semaphore warnings
✅ **After**: File uploads complete successfully, application continues running

You may see this message at startup (this is normal and safe to ignore):
```
huggingface/tokenizers: The current process just got forked, after parallelism has already been used. Disabling parallelism to avoid deadlocks...
```

## Performance Impact

⚠️ **Minimal impact**: Encoding will use single-threaded CPU processing
- For small documents (< 1000 chunks): No noticeable difference
- For large documents: May take slightly longer, but application remains stable

## Alternative: Production Server

For production, consider using a proper WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 1 -b 0.0.0.0:5001 app:app
```

Note: Use `-w 1` (single worker) to avoid multiprocessing issues, or use `-w N` with preload if you need multiple workers.


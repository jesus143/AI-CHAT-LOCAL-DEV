#!/bin/bash

echo "🔥 Starting Flask Backend..."
echo ""

# Set environment variables to prevent multiprocessing issues
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=1

cd python
source venv/bin/activate
python app.py


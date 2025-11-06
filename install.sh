#!/bin/bash

echo "🚀 RAG AI Chat - Installation Script"
echo "===================================="
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null
then
    echo "❌ Ollama is not installed!"
    echo "Please install Ollama from: https://ollama.ai"
    echo "Then run this script again."
    exit 1
else
    echo "✅ Ollama is installed"
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python 3 is not installed!"
    echo "Please install Python 3.8 or higher"
    exit 1
else
    echo "✅ Python 3 is installed"
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null
then
    echo "❌ Node.js is not installed!"
    echo "Please install Node.js 16 or higher"
    exit 1
else
    echo "✅ Node.js is installed"
fi

echo ""
echo "📦 Installing dependencies..."
echo ""

# Install Python dependencies
echo "1️⃣ Setting up Python environment..."
cd python

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "   Created virtual environment"
fi

source venv/bin/activate
pip install -r requirements.txt --quiet
echo "   ✅ Python dependencies installed"

cd ..

# Install Node.js dependencies
echo "2️⃣ Setting up Node.js..."
npm install --silent
echo "   ✅ Node.js dependencies installed"

echo ""
echo "🤖 Pulling Ollama model (phi4-mini:3.8b)..."
ollama pull phi4-mini:3.8b

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To start the application, run these commands in TWO separate terminals:"
echo ""
echo "Terminal 1 (Flask Backend):"
echo "  cd python"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Terminal 2 (Node.js Server):"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo ""


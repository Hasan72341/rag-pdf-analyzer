#!/bin/bash

echo "Starting RAG PDF Analyzer API..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the FastAPI server
uvicorn rag_pdf_fastapi:app --reload --host 0.0.0.0 --port 8000

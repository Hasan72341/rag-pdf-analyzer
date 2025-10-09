#!/bin/bash

echo "Starting RAG PDF Analyzer..."
echo ""

# Check if backend is running
if ! lsof -i :8000 > /dev/null 2>&1; then
    echo "Starting backend API..."
    cd "$(dirname "$0")"
    ./start_api.sh &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
    sleep 3
else
    echo "Backend already running on port 8000"
fi

# Check if frontend is running
if ! lsof -i :3000 > /dev/null 2>&1; then
    echo "Starting frontend..."
    cd "$(dirname "$0")/frontend"
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
else
    echo "Frontend already running on port 3000"
fi

echo ""
echo "================================"
echo "RAG PDF Analyzer is ready!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "================================"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for any process to exit
wait

#!/bin/bash

# Simple GenAI Environment Starter - bypasses credential issues

echo "🚀 Starting GenAI Development Environment (Simple Mode)..."

# Set Docker path and credentials
export PATH="/Applications/Docker.app/Contents/Resources/bin:/usr/local/bin:$PATH"
export DOCKER_BUILDKIT=0  # Disable BuildKit to avoid credential issues

# Use full Docker path
DOCKER_CMD="/usr/local/bin/docker"

# Check Docker is working
if ! $DOCKER_CMD version > /dev/null 2>&1; then
    echo "❌ Docker is not working"
    exit 1
fi

echo "✅ Docker is working"

# Pull required images first
echo "📥 Pre-pulling required images..."
$DOCKER_CMD pull python:3.11-slim
$DOCKER_CMD pull postgres:15
$DOCKER_CMD pull redis:7-alpine
$DOCKER_CMD pull qdrant/qdrant:latest
$DOCKER_CMD pull ollama/ollama:latest

# Now start with compose
echo "📦 Starting containers..."
$DOCKER_CMD compose up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 15

echo ""
echo "🎉 GenAI Development Environment is ready!"
echo ""
echo "📊 Access your services:"
echo "   • Jupyter Lab:    http://localhost:8888 (token: genai-dev-token)"
echo "   • VS Code Server: http://localhost:8080 (password: genai-dev-password)"
echo "   • Streamlit:      http://localhost:8501"
echo "   • Gradio:         http://localhost:7860"
echo ""
echo "💾 Database services:"
echo "   • PostgreSQL:     localhost:5432"
echo "   • Redis:          localhost:6379"
echo "   • Qdrant:         http://localhost:6333"
echo "   • Ollama:         http://localhost:11434"
echo ""
echo "🔧 Next steps:"
echo "   • ./setup-models.sh   - Download AI models"
echo "   • ./stop-env.sh       - Stop environment"
echo "   • ./logs.sh           - View logs"
#!/bin/bash

# GenAI Development Environment - Start Script

echo "🚀 Starting GenAI Development Environment..."

#!/bin/bash

# GenAI Development Environment - Start Script

echo "🚀 Starting GenAI Development Environment..."

# Function to check Docker installation and running status
check_docker() {
    # Common Docker paths on macOS
    DOCKER_PATHS=(
        "/usr/local/bin/docker"
        "/opt/homebrew/bin/docker"
        "/Applications/Docker.app/Contents/Resources/bin/docker"
        "docker"
    )
    
    for docker_cmd in "${DOCKER_PATHS[@]}"; do
        if command -v "$docker_cmd" > /dev/null 2>&1; then
            if "$docker_cmd" version > /dev/null 2>&1; then
                echo "✅ Docker is running (found at: $docker_cmd)"
                # Export Docker command for docker-compose
                export DOCKER_CMD="$docker_cmd"
                return 0
            fi
        fi
    done
    
    echo "❌ Docker is not running or not found in PATH."
    echo "💡 Please make sure:"
    echo "   1. Docker Desktop is installed and running"
    echo "   2. Docker is in your PATH, or try:"
    echo "      export PATH=\"/Applications/Docker.app/Contents/Resources/bin:\$PATH\""
    return 1
}

# Check Docker
if ! check_docker; then
    exit 1
fi

# Build and start the environment
echo "📦 Building and starting containers..."

# Use the Docker path we found earlier
DOCKER_CMD="/usr/local/bin/docker"

# Check which docker compose command is available
if command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif $DOCKER_CMD compose version > /dev/null 2>&1; then
    COMPOSE_CMD="$DOCKER_CMD compose"
else
    echo "❌ Docker Compose is not available"
    echo "💡 Please install Docker Compose"
    exit 1
fi

echo "Using: $COMPOSE_CMD"
$COMPOSE_CMD up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

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
echo "   • Elasticsearch:  http://localhost:9200"
echo "   • Qdrant:         http://localhost:6333"
echo "   • Ollama:         http://localhost:11434"
echo ""
echo "🔧 Useful commands:"
echo "   • ./stop-env.sh       - Stop the environment"
echo "   • ./logs.sh           - View logs"
echo "   • ./shell.sh          - Open shell in container"
echo "   • ./restart-env.sh    - Restart the environment"
echo "   • ./setup-models.sh   - Download AI models (after environment is running)"
echo ""
echo "📁 Your workspace is mounted at /workspace in the container"
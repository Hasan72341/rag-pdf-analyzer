#!/bin/bash

# GenAI Development Environment - Shell Access

echo "🐚 Opening shell in GenAI development container..."

# Check if container is running
if ! docker ps | grep -q "genai-dev-container"; then
    echo "❌ GenAI development container is not running."
    echo "💡 Start it first with: ./start-env.sh"
    exit 1
fi

# Open interactive shell
docker exec -it genai-dev-container /bin/bash
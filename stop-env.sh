#!/bin/bash

# GenAI Development Environment - Stop Script

echo "🛑 Stopping GenAI Development Environment..."

# Use the Docker path we found earlier
DOCKER_CMD="/usr/local/bin/docker"

# Check which docker compose command is available
if command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif $DOCKER_CMD compose version > /dev/null 2>&1; then
    COMPOSE_CMD="$DOCKER_CMD compose"
else
    echo "❌ Docker Compose is not available"
    exit 1
fi

# Stop all containers
$COMPOSE_CMD down

echo "✅ Environment stopped successfully!"
echo ""
echo "💡 To remove all data volumes as well, run:"
echo "   docker-compose down -v"
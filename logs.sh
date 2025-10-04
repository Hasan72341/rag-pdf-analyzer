#!/bin/bash

# GenAI Development Environment - View Logs

echo "📋 Viewing GenAI Development Environment logs..."
echo "Press Ctrl+C to exit log viewing"
echo ""

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

# Show logs for all services
$COMPOSE_CMD logs -f
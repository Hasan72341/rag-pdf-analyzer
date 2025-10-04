#!/bin/bash

# GenAI Development Environment - Restart Script

echo "🔄 Restarting GenAI Development Environment..."

# Stop the environment
./stop-env.sh

echo ""
echo "⏳ Waiting a moment before restart..."
sleep 3

# Start the environment
./start-env.sh
#!/bin/bash

# Docker Path Setup for macOS
echo "🔧 Setting up Docker path for GenAI Development Environment..."

# Common Docker installation paths on macOS
DOCKER_PATHS=(
    "/usr/local/bin"
    "/opt/homebrew/bin"
    "/Applications/Docker.app/Contents/Resources/bin"
)

# Check current PATH
if command -v docker > /dev/null 2>&1; then
    echo "✅ Docker is already in PATH: $(which docker)"
    docker version
    exit 0
fi

echo "🔍 Looking for Docker installation..."

# Search for Docker
for path in "${DOCKER_PATHS[@]}"; do
    if [ -f "$path/docker" ]; then
        echo "✅ Found Docker at: $path/docker"
        
        # Add to current session
        export PATH="$path:$PATH"
        
        # Add to shell profile
        SHELL_PROFILE=""
        if [ -f "$HOME/.zshrc" ]; then
            SHELL_PROFILE="$HOME/.zshrc"
        elif [ -f "$HOME/.bash_profile" ]; then
            SHELL_PROFILE="$HOME/.bash_profile"
        elif [ -f "$HOME/.bashrc" ]; then
            SHELL_PROFILE="$HOME/.bashrc"
        fi
        
        if [ -n "$SHELL_PROFILE" ]; then
            if ! grep -q "$path" "$SHELL_PROFILE"; then
                echo "📝 Adding Docker to $SHELL_PROFILE"
                echo "export PATH=\"$path:\$PATH\"" >> "$SHELL_PROFILE"
            fi
        fi
        
        echo "✅ Docker is now available!"
        docker version
        echo ""
        echo "💡 You may need to restart your terminal or run:"
        echo "   source $SHELL_PROFILE"
        exit 0
    fi
done

echo "❌ Docker not found in common locations."
echo "💡 Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
echo "   Or if already installed, add it to your PATH manually."
exit 1
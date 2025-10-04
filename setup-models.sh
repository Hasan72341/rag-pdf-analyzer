#!/bin/bash

# GenAI Model Setup Script
# Downloads and configures AI models for the development environment

echo "🤖 Setting up AI models for GenAI Development Environment..."

# Function to check if Ollama is running
check_ollama() {
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "❌ Ollama is not running. Please start the environment first with ./start-env.sh"
        exit 1
    fi
}

# Function to pull Ollama model
pull_ollama_model() {
    local model="$1"
    echo "📥 Downloading $model..."
    curl -X POST http://localhost:11434/api/pull -d "{\"name\":\"$model\"}"
    echo ""
}

# Function to list available models
list_models() {
    echo "📋 Available models:"
    curl -s http://localhost:11434/api/tags | python3 -m json.tool
}

# Main menu
echo ""
echo "Choose an option:"
echo "1. Download recommended models (Qwen2.5:7b, Llama3.1:8b, CodeLlama:7b)"
echo "2. Download Qwen2.5:4b (lightweight)"
echo "3. Download Qwen2.5:7b (balanced)"
echo "4. Download Qwen2.5:14b (advanced)"
echo "5. Download Llama3.1:8b"
echo "6. Download CodeLlama:7b (code generation)"
echo "7. Download Mistral:7b"
echo "8. Download Phi3.5:3.8b (lightweight)"
echo "9. List installed models"
echo "10. Custom model (enter model name)"
echo ""

read -p "Enter your choice (1-10): " choice

check_ollama

case $choice in
    1)
        echo "📦 Downloading recommended model set..."
        pull_ollama_model "qwen2.5:7b"
        pull_ollama_model "llama3.1:8b"
        pull_ollama_model "codellama:7b"
        ;;
    2)
        pull_ollama_model "qwen2.5:4b"
        ;;
    3)
        pull_ollama_model "qwen2.5:7b"
        ;;
    4)
        pull_ollama_model "qwen2.5:14b"
        ;;
    5)
        pull_ollama_model "llama3.1:8b"
        ;;
    6)
        pull_ollama_model "codellama:7b"
        ;;
    7)
        pull_ollama_model "mistral:7b"
        ;;
    8)
        pull_ollama_model "phi3.5:3.8b"
        ;;
    9)
        list_models
        ;;
    10)
        read -p "Enter model name (e.g., 'qwen2.5:4b'): " custom_model
        pull_ollama_model "$custom_model"
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "✅ Model setup complete!"
echo ""
echo "🔧 Test your models with:"
echo "   curl -X POST http://localhost:11434/api/generate -d '{\"model\":\"qwen2.5:7b\",\"prompt\":\"Hello, how are you?\"}'"
echo ""
echo "💡 Or use them in Python:"
echo "   import ollama"
echo "   response = ollama.chat(model='qwen2.5:7b', messages=[{'role': 'user', 'content': 'Hello!'}])"
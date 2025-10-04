#!/bin/bash

echo "🚀 Starting GenAI Development Environment..."

# Function to start a service in the background
start_service() {
    local service_name="$1"
    local command="$2"
    echo "Starting $service_name..."
    eval "$command" &
}

# Start Jupyter Lab
start_service "Jupyter Lab" "jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=genai-dev-token"

# Start Code Server (VS Code in browser)
start_service "Code Server" "code-server --bind-addr 0.0.0.0:8080 --auth password"

# Print access information
echo ""
echo "🎉 GenAI Development Environment is starting up!"
echo ""
echo "📊 Services will be available at:"
echo "   • Jupyter Lab:    http://localhost:8888 (token: genai-dev-token)"
echo "   • VS Code Server: http://localhost:8080 (password: genai-dev-password)"
echo "   • Streamlit:      http://localhost:8501"
echo "   • Gradio:         http://localhost:7860"
echo "   • FastAPI/Flask:  http://localhost:5000"
echo "   • General Web:    http://localhost:3000"
echo ""
echo "💾 Database services:"
echo "   • PostgreSQL:     localhost:5432 (user: genai_user, db: genai_db)"
echo "   • Redis:          localhost:6379"
echo "   • Elasticsearch:  http://localhost:9200"
echo "   • Qdrant:         http://localhost:6333 (REST API)"
echo "   • Ollama:         http://localhost:11434 (LLM API)"
echo ""
echo "📁 Workspace structure:"
echo "   • /workspace/projects  - Your AI projects"
echo "   • /workspace/data      - Datasets and data files"
echo "   • /workspace/models    - Trained models and checkpoints"
echo "   • /workspace/notebooks - Jupyter notebooks"
echo ""
echo "🔧 Useful commands:"
echo "   • pip install <package>     - Install Python packages"
echo "   • python your_script.py     - Run Python scripts"
echo "   • streamlit run app.py      - Run Streamlit apps"
echo "   • python -m gradio app.py   - Run Gradio apps"
echo "   • ./setup-models.sh         - Download AI models (Qwen, Llama, etc.)"
echo "   • ollama list               - List installed models"
echo "   • ollama run qwen2.5:7b     - Chat with models directly"
echo ""

# Keep the container running
echo "✅ Environment ready! Press Ctrl+C to stop all services."
wait
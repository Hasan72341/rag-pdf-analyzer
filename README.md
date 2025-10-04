# GenAI Development Environment 🚀

A comprehensive Docker-based development environment for Generative AI, Machine Learning, and LLM applications. This environment includes all the tools and services you need to build, experiment with, and deploy AI applications.

## 🌟 Features

### Core Services
- **Jupyter Lab** - Interactive development environment
- **VS Code Server** - Code editor accessible via browser
- **PostgreSQL with pgvector** - Vector database for embeddings
- **Redis** - Caching and session storage
- **Elasticsearch** - Search and analytics engine
- **Qdrant** - Vector similarity search database
- **Ollama** - Local LLM inference server

### Pre-installed AI Libraries
- **LangChain & LangGraph** - LLM application frameworks
- **OpenAI SDK** - GPT models integration
- **Transformers** - Hugging Face models
- **PyTorch & TensorFlow** - Deep learning frameworks
- **Sentence Transformers** - Text embeddings
- **AutoGen, CrewAI** - Multi-agent frameworks
- **Qdrant, Pinecone, ChromaDB** - Vector database clients

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 8GB RAM (16GB recommended)
- NVIDIA GPU with Docker GPU support (optional, for accelerated inference)

### 1. Clone or Download
```bash
git clone <your-repo> genai-dev
cd genai-dev
```

### 2. Start the Environment
```bash
./start-env.sh
```

### 3. Access Services
Once started, access these services in your browser:

| Service | URL | Credentials |
|---------|-----|-------------|
| Jupyter Lab | http://localhost:8888 | Token: `genai-dev-token` |
| VS Code Server | http://localhost:8080 | Password: `genai-dev-password` |
| Qdrant Dashboard | http://localhost:6333/dashboard | None |
| Elasticsearch | http://localhost:9200 | None |

### 4. Download AI Models
```bash
./setup-models.sh
```
Choose from options like Qwen2.5, Llama3.1, CodeLlama, and more.

## 📁 Project Structure

```
genai-dev/
├── docker-compose.yml      # Main services configuration
├── Dockerfile             # AI development container
├── requirements.txt       # Python dependencies
├── start-env.sh          # Start environment
├── stop-env.sh           # Stop environment
├── setup-models.sh       # Download AI models
├── shell.sh              # Access container shell
├── logs.sh               # View service logs
├── restart-env.sh        # Restart environment
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore file
└── README.md            # This file

Container directories:
├── /workspace/projects   # Your AI projects
├── /workspace/data      # Datasets and data files
├── /workspace/models    # Trained models and checkpoints
└── /workspace/notebooks # Jupyter notebooks
```

## 🛠️ Usage Examples

### Python with OpenAI
```python
import openai
from openai import OpenAI

client = OpenAI(api_key="your-api-key")
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Local LLMs with Ollama
```python
import ollama

# Chat with local model
response = ollama.chat(
    model='qwen2.5:7b',
    messages=[{'role': 'user', 'content': 'Explain quantum computing'}]
)
print(response['message']['content'])
```

### LangChain with Local Models
```python
from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage

llm = OllamaLLM(model="qwen2.5:7b", base_url="http://ollama:11434")
response = llm.invoke("What is machine learning?")
```

### Vector Search with Qdrant
```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Connect to Qdrant
client = QdrantClient(host="qdrant", port=6333)

# Create embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
vectors = model.encode(["Hello world", "AI is amazing"])

# Store and search vectors
# (full example in notebooks/)
```

### LangGraph for Agent Workflows
```python
from langgraph.graph import StateGraph
from langchain_ollama import OllamaLLM

# Build agent workflows with local models
llm = OllamaLLM(model="qwen2.5:7b", base_url="http://ollama:11434")
# (complete agent examples in projects/)
```

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### GPU Support
Uncomment GPU sections in `docker-compose.yml` for NVIDIA GPU acceleration:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

### Custom Models
Add models to Ollama:
```bash
# Inside container or via API
curl -X POST http://localhost:11434/api/pull -d '{"name":"your-model"}'
```

## 📊 Database Connections

### PostgreSQL with pgvector
```python
import psycopg2
conn = psycopg2.connect(
    host="postgres",
    database="genai_db",
    user="genai_user",
    password="genai_password"
)
```

### Redis
```python
import redis
r = redis.Redis(host='redis', port=6379, db=0)
```

### Elasticsearch
```python
from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': 'elasticsearch', 'port': 9200}])
```

## 🚀 Development Workflows

### 1. Jupyter Development
- Open http://localhost:8888
- Create notebooks in `/workspace/notebooks/`
- Use pre-installed libraries for rapid prototyping

### 2. VS Code Development
- Open http://localhost:8080
- Full IDE experience with extensions
- Integrated terminal and debugging

### 3. Streamlit Apps
```bash
streamlit run your_app.py --server.port 8501 --server.address 0.0.0.0
```

### 4. Gradio Apps
```bash
python -m gradio your_app.py --server-port 7860 --server-name 0.0.0.0
```

## 🧪 Example Projects

Check the `/workspace/projects/` directory for:
- RAG (Retrieval Augmented Generation) systems
- Multi-agent applications
- Fine-tuning workflows  
- Vector search implementations
- LangGraph agent workflows

## 🔍 Monitoring and Logs

```bash
# View all service logs
./logs.sh

# Access container shell
./shell.sh

# Check service status
docker-compose ps
```

## 🛡️ Security Notes

- Change default passwords in production
- Use environment variables for API keys
- Don't commit `.env` files to version control
- Review exposed ports for production deployment

## 🤝 Contributing

1. Fork the repository
2. Create feature branches
3. Test changes in the development environment
4. Submit pull requests

## 📚 Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [Ollama Models](https://ollama.ai/library)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Jupyter Lab Guide](https://jupyterlab.readthedocs.io/)

## 📄 License

MIT License - See LICENSE file for details.

---

Happy building! 🚀🤖
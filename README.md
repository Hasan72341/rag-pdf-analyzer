# RAG PDF Analyzer

A full-stack application for analyzing PDF documents using RAG (Retrieval-Augmented Generation) with NVIDIA AI and Qdrant vector database.

## Features

- **PDF Upload**: Upload multiple PDF documents through a clean web interface
- **Intelligent Q&A**: Ask questions and get accurate answers from your documents
- **Vector Search**: Powered by Qdrant for fast semantic search
- **NVIDIA AI**: Uses NVIDIA's LLM and embedding models
- **Modern UI**: React-based responsive frontend with real-time status updates

## Tech Stack

### Backend
- FastAPI (Python web framework)
- LangChain (RAG orchestration)
- Qdrant (Vector database)
- NVIDIA AI API (LLM and embeddings)
- PyPDF2 (PDF processing)

### Frontend
- React 18
- Vite (Build tool)
- Axios (API client)
- Modern CSS with gradients and animations

## Prerequisites

- Python 3.8+
- Node.js 16+
- NVIDIA API key

## Setup

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your NVIDIA_API_KEY
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Option 1: Run Everything Together (Recommended)

```bash
# Make the script executable
chmod +x start_all.sh

# Start both frontend and backend
./start_all.sh
```

### Option 2: Run Separately

**Terminal 1 - Backend:**
```bash
./start_api.sh
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Access Points

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Usage

1. **Upload PDFs**: 
   - Click "Choose File" and select a PDF
   - Click "Upload" to process the document
   - View the list of uploaded documents

2. **Ask Questions**:
   - Type your question in the text area
   - Press Enter or click "Ask"
   - Get AI-generated answers based on your documents

## API Endpoints

- `GET /health` - Check system health
- `POST /upload-pdf` - Upload a PDF document
- `POST /query` - Query the documents
- `GET /documents` - List uploaded documents

## Project Structure

```
.
├── rag_pdf_fastapi.py      # Backend API
├── requirements.txt         # Python dependencies
├── start_api.sh            # Backend startup script
├── start_all.sh            # Run everything
├── .env                    # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.css         # Styles
│   │   ├── api.js          # API client
│   │   └── main.jsx        # Entry point
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
└── setup/
    └── *.pdf               # Sample PDFs
```

## Development

### Backend Development
- The backend uses FastAPI with auto-reload enabled
- Changes to Python files will automatically restart the server

### Frontend Development
- Vite provides hot module replacement (HMR)
- Changes to React components update instantly in the browser

## Troubleshooting

**Backend won't start:**
- Check if port 8000 is available: `lsof -i :8000`
- Verify NVIDIA_API_KEY in .env
- Ensure Qdrant is accessible

**Frontend won't start:**
- Check if port 3000 is available: `lsof -i :3000`
- Run `npm install` in the frontend directory
- Clear npm cache: `npm cache clean --force`

**Can't query documents:**
- Ensure you've uploaded at least one PDF
- Check backend logs for errors
- Verify API connection in browser console

## License

MIT

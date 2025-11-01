import os
import io
import uuid
import logging
import sys
from typing import List, Optional, Dict, Any, Set

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.embeddings.base import Embeddings
from PyPDF2 import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from openai import OpenAI
import sqlite3
from datetime import datetime

load_dotenv()

app = FastAPI(
    title="RAG PDF Analyzer API",
    description="Upload PDFs and query their content using AI-powered retrieval",
    version="1.0.0"
)
class QueryRequest(BaseModel):
    question: str
    max_chunks: Optional[int] = 3

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_created: int
    success: bool

g_analyzer = None

class NVIDIAEmbeddings(Embeddings):
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
            extra_body={"input_type": "passage"}
        )
        return [data.embedding for data in response.data]
    
    def embed_query(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=[text],
            extra_body={"input_type": "query"}
        )
        return response.data[0].embedding

class RAGPDFAnalyzer:
    def __init__(self):
        self._configure_logging()
        self._init_embeddings()
        self._init_llm()
        self._init_text_splitter()
        self._init_qdrant()
        # track uploaded document filenames
        self.documents: Set[str] = set()
    
    def _init_embeddings(self):
        self.embeddings = NVIDIAEmbeddings(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
            model="nvidia/nv-embedqa-e5-v5"
        )
        
    def _init_llm(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE"),
            model="meta/llama-3.3-70b-instruct",
            temperature=0.3
        )
        
    def _init_text_splitter(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
    def _init_qdrant(self):
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_client = QdrantClient(url=qdrant_url)
        self.collection_name = "pdf_documents"
        
        try:
            self.qdrant_client.get_collection(self.collection_name)
        except:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
            )
        # initialize sqlite metadata DB
        self._init_metadata_db()

    def _init_metadata_db(self) -> None:
        db_path = os.getenv("METADATA_DB", "./documents_meta.db")
        self._db_conn = sqlite3.connect(db_path, check_same_thread=False)
        cur = self._db_conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                filename TEXT PRIMARY KEY,
                chunks INTEGER,
                uploaded_at TEXT
            )
            """
        )
        self._db_conn.commit()
    
    def extract_text_from_pdf(self, pdf_content: bytes, filename: str) -> str:
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                logging.exception("Error extracting text from page in %s: %s", filename, e)
        return text
    
    def process_and_store_pdf(self, pdf_content: bytes, filename: str) -> dict:
        text = self.extract_text_from_pdf(pdf_content, filename)
        if not text.strip():
            raise ValueError("No extractable text found in PDF")

        chunks = self.text_splitter.split_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "source": filename,
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "document_id": str(uuid.uuid4())
                }
            )
            documents.append(doc)
        # When adding documents to Qdrant we include simple payload data so
        # we can list documents later. Langchain's Qdrant wrapper will map
        # metadata into payloads.
        vectorstore = Qdrant(
            client=self.qdrant_client,
            collection_name=self.collection_name,
            embeddings=self.embeddings
        )

        vectorstore.add_documents(documents)
        # record document in-memory
        self.documents.add(filename)
        # persist metadata
        try:
            cur = self._db_conn.cursor()
            cur.execute(
                "REPLACE INTO documents (filename, chunks, uploaded_at) VALUES (?, ?, ?)",
                (filename, len(chunks), datetime.utcnow().isoformat()),
            )
            self._db_conn.commit()
        except Exception:
            logging.exception("Failed to persist metadata for %s", filename)

        return {
            "success": True,
            "chunks_created": len(chunks),
            "filename": filename
        }

    def query_documents(self, question: str, max_chunks: int = 3) -> dict:
        vectorstore = Qdrant(
            client=self.qdrant_client,
            collection_name=self.collection_name,
            embeddings=self.embeddings
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": max_chunks}),
            return_source_documents=True
        )
        
        try:
            result = qa_chain.invoke({"query": question})
        except Exception as e:
            logging.exception("Error running QA chain for question: %s", question)
            raise
        
        sources = []
        for doc in result.get("source_documents", []):
            source_info = {
                "source": doc.metadata.get("source", "Unknown"),
                "chunk_id": doc.metadata.get("chunk_id", 0),
                "content_preview": doc.page_content[:200] + "...",
                "full_content": doc.page_content
            }
            sources.append(source_info)
        
        return {
            "answer": result.get("result", ""),
            "sources": sources
        }
    
    def get_collection_info(self) -> dict:
        try:
            info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "total_documents": getattr(info, "points_count", 0),
                "collection_name": self.collection_name
            }
        except:
            return {"total_documents": 0, "collection_name": self.collection_name}

    def list_documents(self) -> List[str]:
        """Return a list of unique document filenames stored in the collection.

        This queries Qdrant payloads for the `source` field and falls back to
        the in-memory set when Qdrant is unavailable.
        """
        try:
            cur = self._db_conn.cursor()
            cur.execute("SELECT filename FROM documents ORDER BY uploaded_at DESC")
            rows = cur.fetchall()
            return [r[0] for r in rows]
        except Exception:
            logging.exception("Failed to read metadata DB, falling back to memory")
            return list(self.documents)

    def _configure_logging(self) -> None:
        # Basic logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s - %(message)s",
            stream=sys.stdout,
        )
        logging.getLogger("uvicorn").setLevel(logging.INFO)

@app.on_event("startup")
async def startup_event():
    global g_analyzer
    g_analyzer = RAGPDFAnalyzer()

@app.get("/")
async def root():
    return {
        "message": "RAG PDF Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload-pdf",
            "query": "/query",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    if g_analyzer is None:
        return {
            "status": "initializing",
            "qdrant_connected": False,
            "documents_stored": 0
        }
    
    try:
        info = g_analyzer.get_collection_info()
        return {
            "status": "healthy",
            "qdrant_connected": True,
            "documents_stored": info["total_documents"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "qdrant_connected": False
        }

@app.post("/upload-pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if g_analyzer is None:
        raise HTTPException(status_code=503, detail="Service not ready. Please wait for initialization.")
    
    content = await file.read()
    result = g_analyzer.process_and_store_pdf(content, file.filename)
    
    return UploadResponse(
        message=f"Successfully processed {file.filename}",
        filename=file.filename,
        chunks_created=result["chunks_created"],
        success=True
    )

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    if g_analyzer is None:
        raise HTTPException(status_code=503, detail="Service not ready. Please wait for initialization.")
    
    result = g_analyzer.query_documents(request.question, request.max_chunks)
    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"]
    )

@app.get("/documents")
async def get_documents_info():
    info = g_analyzer.get_collection_info()
    documents = g_analyzer.list_documents() if g_analyzer else []
    return {
        "documents": documents,
        "total_chunks": info["total_documents"],
        "collection_name": info["collection_name"]
    }

@app.delete("/documents")
async def clear_documents():
    # Delete collection and recreate an empty one to ensure the service stays
    # usable after clearing. Also clear the in-memory tracking.
    try:
        g_analyzer.qdrant_client.delete_collection(g_analyzer.collection_name)
    except Exception:
        # ignore if already removed
        pass

    # recreate collection
    g_analyzer.qdrant_client.create_collection(
        collection_name=g_analyzer.collection_name,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )

    g_analyzer.documents.clear()
    # clear metadata DB
    try:
        cur = g_analyzer._db_conn.cursor()
        cur.execute("DELETE FROM documents")
        g_analyzer._db_conn.commit()
    except Exception:
        logging.exception("Failed to clear metadata DB")

    return {"message": "All documents cleared successfully", "documents": []}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
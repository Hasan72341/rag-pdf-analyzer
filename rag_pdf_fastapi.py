import os
import io
import uuid
from typing import List, Optional
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
        self._init_embeddings()
        self._init_llm()
        self._init_text_splitter()
        self._init_qdrant()
    
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
        self.qdrant_client = QdrantClient(url="http://localhost:6333")
        self.collection_name = "pdf_documents"
        
        try:
            self.qdrant_client.get_collection(self.collection_name)
        except:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
            )
    
    def extract_text_from_pdf(self, pdf_content: bytes, filename: str) -> str:
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    def process_and_store_pdf(self, pdf_content: bytes, filename: str) -> dict:
        text = self.extract_text_from_pdf(pdf_content, filename)
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
        
        vectorstore = Qdrant(
            client=self.qdrant_client,
            collection_name=self.collection_name,
            embeddings=self.embeddings
        )
        
        vectorstore.add_documents(documents)
        
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
        
        result = qa_chain({"query": question})
        
        sources = []
        for doc in result["source_documents"]:
            source_info = {
                "source": doc.metadata.get("source", "Unknown"),
                "chunk_id": doc.metadata.get("chunk_id", 0),
                "content_preview": doc.page_content[:200] + "...",
                "full_content": doc.page_content
            }
            sources.append(source_info)
        
        return {
            "answer": result["result"],
            "sources": sources
        }
    
    def get_collection_info(self) -> dict:
        try:
            info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "total_documents": info.points_count,
                "collection_name": self.collection_name
            }
        except:
            return {"total_documents": 0, "collection_name": self.collection_name}

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
    return {
        "total_chunks": info["total_documents"],
        "collection_name": info["collection_name"]
    }

@app.delete("/documents")
async def clear_documents():
    g_analyzer.qdrant_client.delete_collection(g_analyzer.collection_name)
    return {"message": "All documents cleared successfully"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
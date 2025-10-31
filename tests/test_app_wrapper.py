from fastapi import FastAPI, UploadFile, File
from fastapi.testclient import TestClient
import io


class FakeAnalyzer:
    def __init__(self):
        self.documents = set()

    def get_collection_info(self):
        return {"total_documents": 0, "collection_name": "pdf_documents"}

    def list_documents(self):
        return list(self.documents)

    def process_and_store_pdf(self, pdf_content: bytes, filename: str):
        self.documents.add(filename)
        return {"success": True, "chunks_created": 1, "filename": filename}


app = FastAPI()
analyzer = FakeAnalyzer()


@app.get("/health")
def health():
    info = analyzer.get_collection_info()
    return {"status": "healthy", "qdrant_connected": True, "documents_stored": info['total_documents']}


@app.post("/upload-pdf")
def upload(file: UploadFile = File(...)):
    content = file.file.read()
    result = analyzer.process_and_store_pdf(content, file.filename)
    return result


@app.get("/documents")
def documents():
    return {"documents": analyzer.list_documents(), "total_chunks": 0, "collection_name": "pdf_documents"}


@app.delete("/documents")
def delete_documents():
    analyzer.documents.clear()
    return {"message": "All documents cleared successfully", "documents": []}


client = TestClient(app)

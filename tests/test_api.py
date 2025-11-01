import io
import os
import tempfile
from fastapi.testclient import TestClient

from test_app_wrapper import client


def test_health_initializing():
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'healthy'


def test_upload_and_list_and_delete():
    # Create a small fake PDF (just bytes)
    pdf_bytes = b"%PDF-1.4\n%fake pdf content"
    files = {'file': ('sample.pdf', io.BytesIO(pdf_bytes), 'application/pdf')}

    res = client.post('/upload-pdf', files=files)
    assert res.status_code == 200
    data = res.json()
    assert data['success'] is True
    assert data['chunks_created'] == 1

    res = client.get('/documents')
    assert res.status_code == 200
    doc_data = res.json()
    assert 'documents' in doc_data

    # delete
    res = client.delete('/documents')
    assert res.status_code == 200
    assert res.json()['documents'] == []

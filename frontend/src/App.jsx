import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { healthCheck, uploadPDF, queryDocuments, listDocuments } from './api';
import './App.css';

function App() {
  const [health, setHealth] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [querying, setQuerying] = useState(false);
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    checkHealth();
    loadDocuments();
  }, []);

  const checkHealth = async () => {
    try {
      const data = await healthCheck();
      setHealth(data);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealth({ status: 'error', message: error.message });
    }
  };

  const loadDocuments = async () => {
    try {
      const data = await listDocuments();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setUploadMessage('');
    } else {
      setSelectedFile(null);
      setUploadMessage('Please select a valid PDF file');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadMessage('Please select a file first');
      return;
    }

    setUploading(true);
    setUploadMessage('');

    try {
      const data = await uploadPDF(selectedFile);
      setUploadMessage(`Success! Uploaded ${data.chunks_added} chunks from ${data.filename}`);
      setSelectedFile(null);
      document.getElementById('fileInput').value = '';
      await loadDocuments();
    } catch (error) {
      setUploadMessage(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async () => {
    if (!question.trim()) {
      setAnswer('Please enter a question');
      return;
    }

    setQuerying(true);
    setAnswer('');

    try {
      const data = await queryDocuments(question);
      setAnswer(data.answer);
    } catch (error) {
      setAnswer(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setQuerying(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleQuery();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>RAG PDF Analyzer</h1>
        <div className="health-status">
          {health ? (
            <span className={`status-badge ${health.status}`}>
              {health.status === 'healthy' ? '✓' : '✗'} {health.status}
              {health.document_count !== undefined && ` · ${health.document_count} docs`}
            </span>
          ) : (
            <span className="status-badge loading">Loading...</span>
          )}
        </div>
      </header>

      <main className="main">
        <section className="upload-section">
          <h2>Upload PDF</h2>
          <div className="upload-container">
            <input
              id="fileInput"
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              className="file-input"
            />
            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className="button primary"
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
          {uploadMessage && (
            <div className={`message ${uploadMessage.startsWith('Success') ? 'success' : 'error'}`}>
              {uploadMessage}
            </div>
          )}
          {documents.length > 0 && (
            <div className="documents-list">
              <h3>Uploaded Documents ({documents.length})</h3>
              <ul>
                {documents.map((doc, index) => (
                  <li key={index}>{doc}</li>
                ))}
              </ul>
            </div>
          )}
        </section>

        <section className="query-section">
          <h2>Ask Questions</h2>
          <div className="query-container">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your uploaded PDFs..."
              className="question-input"
              rows="3"
            />
            <button
              onClick={handleQuery}
              disabled={!question.trim() || querying}
              className="button primary"
            >
              {querying ? 'Searching...' : 'Ask'}
            </button>
          </div>
          {answer && (
            <div className="answer-container">
              <h3>Answer:</h3>
              <div className="answer markdown-content">
                <ReactMarkdown>{answer}</ReactMarkdown>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;

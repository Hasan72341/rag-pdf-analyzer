import axios from 'axios';

// Allow overriding the API base URL via environment variable set by Vite
const API_BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export const healthCheck = async () => {
  const response = await axios.get(`${API_BASE_URL}/health`);
  return response.data;
};

export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_BASE_URL}/upload-pdf`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const queryDocuments = async (question) => {
  const response = await axios.post(`${API_BASE_URL}/query`, {
    question: question,
  });
  return response.data;
};

export const listDocuments = async () => {
  const response = await axios.get(`${API_BASE_URL}/documents`);
  // normalize to an array of filenames
  const data = response.data || {};
  if (Array.isArray(data.documents)) return data.documents;
  // older backend returned total_chunks and collection_name
  return [];
};

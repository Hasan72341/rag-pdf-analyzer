import axios from 'axios';

const API_BASE_URL = '/api';

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
  return response.data;
};

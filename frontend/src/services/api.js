import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

// Add a request interceptor to add the auth token to requests
api.interceptors.request.use(
  (config) => {
    // Remove any existing /api/v1 prefix to prevent duplication
    let url = config.url.replace(/^\/?(api\/v1\/?)+/, '');
    
    // Add api/v1 prefix if not present
    if (!url.startsWith('/')) {
      url = '/' + url;
    }
    config.url = '/api/v1' + url;
    
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Vault endpoints
export const getVaultEntries = (page = 1, limit = 10) => api.get(`/mock/vault/mock?page=${page}&limit=${limit}`);
export const getVaultEntry = (id) => api.get(`/mock/vault/entries/${id}`);
export const archiveVaultEntry = (id) => api.post(`/mock/vault/entries/${id}/archive`);
export const addVaultFeedback = (id, feedback) => api.post(`/mock/vault/entries/${id}/feedback`, feedback);
export const revertRedaction = (id) => api.post(`/mock/vault/revert/${id}`);

export default api; 
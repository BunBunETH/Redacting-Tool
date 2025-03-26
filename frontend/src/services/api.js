import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to add /api/v1 prefix to all requests
api.interceptors.request.use(
  (config) => {
    // Add /api/v1 prefix if not already present
    if (!config.url.startsWith('/api/v1')) {
      config.url = `/api/v1${config.url}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a request interceptor to add the auth token to requests
api.interceptors.request.use(
  (config) => {
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
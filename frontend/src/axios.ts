// src/axios.ts
import axios, { AxiosInstance } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000', // Your backend URL
});

// Add Authorization Token Interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token'); // Assuming the token is stored in localStorage
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api; 
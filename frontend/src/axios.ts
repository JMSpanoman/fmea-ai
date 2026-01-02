// src/axios.ts
import axios, { AxiosInstance, AxiosError } from 'axios';

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000', // Your backend URL
});

// Helper function to get a fresh token
async function ensureValidToken(): Promise<string | null> {
  let token = localStorage.getItem('token');
  
  // If no token, try to get one via dev-login
  if (!token) {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/auth/dev-login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        token = data.access_token;
        if (token) {
          localStorage.setItem('token', token);
        }
      }
    } catch (error) {
      console.error('Failed to get auth token:', error);
    }
  }
  
  return token;
}

// Add Authorization Token Interceptor
api.interceptors.request.use(
  async (config) => {
    const token = await ensureValidToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add Response Interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    
    // If we get a 401 and haven't retried yet, try to refresh the token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Get a fresh token
        const token = await ensureValidToken();
        
        if (token) {
          // Retry the original request with the new token
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        console.error('Failed to refresh token:', refreshError);
        // If refresh fails, reject the promise
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api; 
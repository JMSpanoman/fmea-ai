// src/axios.ts
import axios, { AxiosInstance, AxiosError } from 'axios';

// Use VITE_API_URL or VITE_API_BASE_URL, fallback to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 
                     import.meta.env.VITE_API_BASE_URL || 
                     'http://localhost:8000';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

// Helper function to get a fresh token via dev-login
async function ensureValidToken(): Promise<string | null> {
  let token = localStorage.getItem('token');
  
  // If no token, try to get one via dev-login
  if (!token) {
    try {
      console.log('[axios] No token found, attempting dev-login...');
      const devEmail = localStorage.getItem('dev_login_email') || '';
      // Use native fetch to avoid circular dependency
      const response = await fetch(`${API_BASE_URL}/auth/dev-login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: devEmail ? JSON.stringify({ email: devEmail }) : undefined,
      });
      
      if (response.ok) {
        const data = await response.json();
        token = data.access_token;
        if (token) {
          localStorage.setItem('token', token);
          console.log('[axios] Token obtained via dev-login and stored in localStorage');
        } else {
          console.error('[axios] No access_token in dev-login response:', data);
        }
      } else {
        const errorText = await response.text().catch(() => 'Unknown error');
        console.error('[axios] Failed to get auth token: HTTP', response.status, errorText);
      }
    } catch (error) {
      console.error('[axios] Failed to get auth token:', error);
    }
  } else {
    console.log('[axios] Using existing token from localStorage');
  }
  
  return token;
}

// Add Authorization Token Interceptor
api.interceptors.request.use(
  async (config) => {
    const token = await ensureValidToken();
    
    // Debug logging for /projects endpoint
    if (config.url?.includes('/projects') && !config.url.includes('/projects/')) {
      console.log('[axios] Request to /projects - Authorization header:', token ? 'attached' : 'missing');
    }
    
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    } else {
      console.warn('[axios] No token available for request to', config.url);
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
        // Clear old token
        localStorage.removeItem('token');
        
        // Get a fresh token
        const token = await ensureValidToken();
        
        if (token) {
          // Retry the original request with the new token
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          return api(originalRequest);
        } else {
          console.error('[axios] Failed to refresh token after 401');
        }
      } catch (refreshError) {
        console.error('[axios] Failed to refresh token:', refreshError);
        // If refresh fails, reject the promise
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
export { API_BASE_URL }; 
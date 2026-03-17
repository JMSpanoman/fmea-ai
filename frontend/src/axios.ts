// src/axios.ts
import axios, { AxiosInstance, AxiosError } from 'axios';

// Single source of truth: VITE_API_BASE_URL when present; otherwise use /api which is proxied
// in dev (Vite proxy) and prod (nginx -> BACKEND_URL).
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

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
      if (!devEmail) {
        // Avoid implicit "dev@example.com" logins; require an explicit user choice.
        return null;
      }
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

// Add Response Interceptor to handle 401 and 403 (Pro upgrade) errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // 403: Pro feature gate — emit event so UI can show upgrade message
    if (error.response?.status === 403) {
      const detail = (error.response?.data as any)?.detail;
      const isProGate = typeof detail === 'string' && /pro|plan|upgrade/i.test(detail);
      if (isProGate) {
        window.dispatchEvent(new CustomEvent('api:403:pro', { detail: { message: detail } }));
      }
    }

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
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
export { API_BASE_URL }; 
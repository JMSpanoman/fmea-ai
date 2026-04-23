import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      external: [],
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: false,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/postmarket': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/fmea': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  // Same proxy as dev so `npm run preview` can talk to the local API (full production bundle).
  preview: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: false,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/postmarket': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/fmea': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});

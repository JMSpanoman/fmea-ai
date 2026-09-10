import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

const proxy = {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path: string) => path.replace(/^\/api/, ''),
  },
  '/postmarket': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
  '/fmea': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
};

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
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
    proxy,
  },
  preview: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: false,
    proxy,
  },
});

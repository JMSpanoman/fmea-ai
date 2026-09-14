import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

const apiProxyTarget = process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000';

const proxy = {
  '/api': {
    target: apiProxyTarget,
    changeOrigin: true,
    rewrite: (path: string) => path.replace(/^\/api/, ''),
  },
  '/postmarket': {
    target: apiProxyTarget,
    changeOrigin: true,
  },
  '/fmea': {
    target: apiProxyTarget,
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
    // Quick tunnels (Cloudflare) send a public Host header; allow them for demos.
    allowedHosts: ['.trycloudflare.com'],
  },
  preview: {
    port: 5173,
    host: '0.0.0.0',
    strictPort: false,
    proxy,
    allowedHosts: ['.trycloudflare.com'],
  },
});

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@store': path.resolve(__dirname, './src/store'),
      '@services': path.resolve(__dirname, './src/services'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@types': path.resolve(__dirname, './src/types'),
    },
  },
  server: {
    port: 16000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:16210',
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'http://localhost:16210',
        changeOrigin: true,
        ws: true,
      },
    },
  },
})

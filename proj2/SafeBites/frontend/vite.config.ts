import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import path from 'path'

export default defineConfig({
  root: '.', // ensure Vite root is the frontend folder
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'), // optional but helpful
    },
  },
  build: {
    outDir: 'dist', // standard output folder
  },
})

import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  server: {
    host: '0.0.0.0', // ✅ allows external access (not just localhost)
    port: 3000,      // ✅ keeps your existing port
    allowedHosts: [
      'fantasykenya.com', // ✅ allow your domain
      'www.fantasykenya.com',
    ],
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})


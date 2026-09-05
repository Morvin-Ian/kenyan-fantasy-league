import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Service names on the compose network; override when running Vite on the host.
const apiTarget = process.env.VITE_API_PROXY_TARGET || 'http://api:8000'
const filesTarget = process.env.VITE_FILES_PROXY_TARGET || 'http://nginx:80'

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
    // Without these the dev server answers /api/v1/... with index.html, so
    // every request resolves to the router's catch-all and the app renders its
    // "Page Not Found" view instead of ever reaching Django.
    //
    // changeOrigin is deliberately left off: forwarding the original Host
    // ("localhost:3000") keeps Django's ALLOWED_HOSTS check happy, whereas
    // rewriting it to "api" — which is not an allowed host — returns 400.
    proxy: {
      '/api': { target: apiTarget },
      '/guardian': { target: apiTarget },
      // Uploaded media and collected static are served by nginx off the shared
      // volumes, not by Django — Django only serves them when DEBUG is on.
      // Routing these through nginx makes team badges load on :3000 whatever
      // DEBUG is set to.
      '/mediafiles': { target: filesTarget },
      '/staticfiles': { target: filesTarget },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})


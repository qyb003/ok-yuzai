import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"
import pkg from "./package.json"

export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
  },
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        entryFileNames: `assets/[name]-[hash]-${Date.now()}.js`,
        chunkFileNames: `assets/[name]-[hash]-${Date.now()}.js`,
        assetFileNames: `assets/[name]-[hash]-${Date.now()}.[ext]`
      }
    }
  },
  server: {
    host: "0.0.0.0",
    port: 5173,  // [DEV] Vite dev server 端口改为 5173（避免与后端 8802 冲突）
    allowedHosts: true,
    proxy: {
      '/api': {
        // [DEV] Docker 内用 app:8802，宿主机本地开发用 127.0.0.1:8802
        target: process.env.VITE_API_TARGET || 'http://127.0.0.1:8802',
        changeOrigin: true,
      },
      '/ws': {
        target: (process.env.VITE_API_TARGET || 'http://127.0.0.1:8802').replace('http', 'ws'),
        changeOrigin: true,
        ws: true,
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./app"),
    },
  },
})

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url' // 1. 新增：引入 Node 的 URL 解析模块

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],

  // 2. 新增：配置解析规则
  resolve: {
    alias: {
      // 告诉 Vite：将 '@' 映射到当前目录下的 'src' 文件夹
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },

  server: {
    proxy: {
      // 当你请求 /api/user/login时，Vite会自动帮你把请求转发给后端
      '/api' : {
        target: 'http://127.0.0.1:5003',
        changeOrigin: true,
        secure: false, // 极其重要：这会忽略ARL本地自签名的HTTPS证书错误。
      }
    }
  }
})
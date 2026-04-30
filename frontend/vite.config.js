import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server:{
    proxy:{
      //当你请求 /api/user/login时，Vite会自动帮你把请求转发给后端
      '/api' :{
        target: 'http://127.0.0.1:5003',
        changeOrigin: true,
        secure: false, // 极其重要：这会忽略ARL本地自签名的HTTPS证书错误。
      }
    }
  }
})

import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css' // Vue3/Antd4 的样式引入方式
import router from './router'

const app = createApp(App)
app.use(router)
app.use(Antd)
app.mount('#app')

import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import Vision from '@wyxos/vision'

createApp(App)
    .use(Vision).mount('#app')

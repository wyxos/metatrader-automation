import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import Vision from '@wyxos/vision'
import '@oruga-ui/theme-oruga/dist/oruga.css'

createApp(App)
    .use(Vision).mount('#app')

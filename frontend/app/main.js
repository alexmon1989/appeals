import { createApp } from 'vue'
import Hello from './components/Hello.vue'

const app = createApp({
    components: {
        Hello,
    }
})

app.mount('#app')
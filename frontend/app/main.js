import { createApp } from 'vue'
import ApplicantFillingForm from './components/ApplicantFillingForm/ApplicantFillingForm.vue'

const app = createApp({
    components: {
        ApplicantFillingForm,
    }
})

app.mount('#app')
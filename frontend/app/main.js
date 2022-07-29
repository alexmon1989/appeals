import { createApp } from 'vue'
import ApplicantFillingForm from './components/ApplicantFillingForm/ApplicantFillingForm.vue'
import AuthForm from './components/AuthForm/AuthForm.vue'
import ClaimAttachments from './components/Attachments/ClaimAttachments.vue'
import ClaimDetails from './components/ClaimDetails/ClaimDetails.vue'
import ClaimsDataTable from './components/ClaimsDataTable/ClaimsDataTable.vue'
import CasesList from './components/CasesList/CasesList.vue'
import CaseStages from './components/CasesDetail/CaseStages.vue'
import { defineRule, configure } from 'vee-validate'
import AllRules from '@vee-validate/rules'
import { localize, setLocale } from '@vee-validate/i18n'
import uk from '@vee-validate/i18n/dist/locale/uk.json'

Object.keys(AllRules).forEach(rule => {
  defineRule(rule, AllRules[rule]);
});

configure({
  generateMessage: localize({
    uk,
  }),
});

setLocale('uk');

const app = createApp({
    components: {
        ApplicantFillingForm,
        AuthForm,
        ClaimAttachments,
        ClaimDetails,
        ClaimsDataTable,
        CasesList,
        CaseStages,
    }
})

app.mount('#app')

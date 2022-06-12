<template>
  <div class="p-4 p-md-5 card rounded-xl">

    <eds-read @edsReaded="onEdsReaded" @tabChange="onTabChange"></eds-read>

    <div class="row mt-3">
      <div class="col-12 mt-1">
        <button type="submit"
                :disabled="!canContinue"
                class="btn btn-secondary w-100 fw-medium"
                @click="login"
        >Продовжити</button>
      </div>
    </div>
  </div>
</template>

<script>
import EdsRead from './EdsRead.vue'
import { getCookie } from '@/app/lib/until'

export default {
  name: "AuthForm",

  components: {
    EdsRead,
  },

  data() {
    return {
      canContinue: false
    }
  },

  methods: {
    onEdsReaded() {
      this.canContinue = true
      $.SOW.core.toast.show('success-soft',
          '',
          'Ключ успішно прочитано. Натисніть <b>"Продовжити"</b> для авторизації у системі.',
          'top-end',
          0,
          true)
    },

    onTabChange() {
      this.canContinue = false
    },

    async login() {
      // const csrftoken = document.getElementsByName('csrfmiddlewaretoken')[0].value
      const csrftoken = getCookie('csrftoken')
      try {
        const response = await fetch('/users/login/', {
          method: 'POST',
          body: JSON.stringify(this.$root.keyInfo),
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
          }
        })
        const json = await response.json()
        if (parseInt(json.is_logged) === 1) {
          location.href = '/filling/'

          const queryString = window.location.search
          const urlParams = new URLSearchParams(queryString)
          const next = urlParams.get('next')

          if (next) {
            location.href = next
          } else {
            location.href = '/filling/'
          }
        } else {
          $.SOW.core.toast.show('danger',
              '',
              'Авторизація неможлива.',
              'top-end',
              0,
              true)
        }
      } catch (e) {
        console.log(e)
        $.SOW.core.toast.show('danger-soft',
            '',
            'Авторизація неможлива.',
            'top-end',
            0,
            true)
      }
    },


  }
}
</script>

<style scoped>

</style>
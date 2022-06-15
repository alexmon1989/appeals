<template>
  <div>
    <table class="table table-striped table-sm">
      <thead>
      <tr>
        <th scope="col">#</th>
        <th scope="col">Тип (назва) документу</th>
        <th scope="col" class="text-center">Сгенеровано автоматично</th>
        <th scope="col">Файл</th>
        <th scope="col" class="text-center">Підписано КЕП</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(document, index) in documents">
        <td class="fw-bold" v-html="index + 1"></td>
        <td>{{ document.document_name }}</td>
        <td class="text-center">
          <span class="text-primary fw-bold" v-if="document.auto_generated">так</span>
          <span v-else>ні</span>
        </td>
        <td>
          <a :href="document.file_url" target="_blank">{{ document.file_name }}</a>
        </td>
        <td class="text-center">
          <span class="text-success fw-bold" v-if="document.sign__count">так</span>
          <span class="text-danger fw-bold" v-else>ні</span>
        </td>
      </tr>
      </tbody>
    </table>

    <div class="d-flex justify-content-end" v-if="needsSign">
      <button class="btn btn-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#exampleModalLg">
        <svg width="16px" height="16px" xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-pen-fill" viewBox="0 0 16 16">
          <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001z"></path>
        </svg>
        <span class="ms-1">Підписати КЕП</span>
      </button>
    </div>

    <ModalEDS :documents-init="documents" @signedDoc="onSignedDocument" @signedAll="onSignedAll"></ModalEDS>
  </div>
</template>

<script>
import ModalEDS from './ModalEDS.vue'

export default {
  name: "ClaimAttachments",
  props: {
    'documentsInit': Array,
    'claimId': Number,
  },
  components: {
    ModalEDS,
  },
  data() {
    return {
      documents: []
    }
  },
  mounted() {
    this.documents = this.documentsInit
  },
  computed: {
    needsSign() {
      const noSign = (document) => document.sign__count === 0
      return this.documents.some(noSign)
    }
  },
  methods: {
    onSignedDocument(value) {
      const document = this.documents.find(item => item.id === value.id)

      $.SOW.core.toast.show('success-soft',
          '',
          'Документ <b>' + document.document_name + '</b> успішно підписано.' ,
          'top-end',
          0,
          true
      )

      document.sign__count++
      document.eds = value.eds
    },

    async onSignedAll() {
      $.SOW.core.toast.show('success-soft',
          '',
          'Усі документи успішно підписано. Ви можете закрити вікно підписання та продовжити роботу.' ,
          'top-end',
          0,
          true
      )

      let response = await fetch('/filling/claim-status/' + this.claimId + '/')
      if (response.ok) {
        let json = await response.json()
        if (json.success === 1) {
          const el = document.getElementById('claim-status')
          if (json.data.status_code === 1) {
            el.innerHTML = 'Статус: <span class="text-danger ms-1">' + json.data.status_verbal + '</span>'
          } else if (json.data.status_code === 2) {
            el.innerHTML = 'Статус: <span class="text-primary ms-1">' + json.data.status_verbal + '</span>'
          } else {
            el.innerHTML = 'Статус: <span class="text-success ms-1">' + json.data.status_verbal + '</span>'
          }
        }
      } else {
        console.log("Error getting claim status: " + response.status)
      }
    }
  }
}
</script>

<style scoped>

</style>
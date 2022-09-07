<template>
  <div v-if="needsSign">
    <div class="d-flex justify-content-end my-4">
      <div class="d-flex justify-content-end">
        <button class="btn btn-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#exampleModalLg">
          <svg width="16px" height="16px" xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-pen-fill"
               viewBox="0 0 16 16">
            <path
                d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001z"></path>
          </svg>
          <span class="ms-1">Підписати КЕП</span>
        </button>
      </div>
    </div>
  </div>

  <ModalEDS :documents-init="documents"
            :case-id="caseId"
            @signedDoc="onSignedDocument"
            @signedAll="onSignedAll"></ModalEDS>
</template>

<script>
import ModalEDS from './ModalEDS.vue'

export default {
  name: "SignDocuments",
  components: {
    ModalEDS
  },
  props: ["documentsInit", "caseId"],
  data() {
    return {
      documents: [],
      needsSign: false
    }
  },
  mounted() {
    if (this.documentsInit.length > 0) {
      this.needsSign = true
    }
    this.documents = this.documentsInit
  },
  methods: {
    onSignedDocument(value) {
      const document = this.documents.find(item => item.id === value.id)

      $.SOW.core.toast.show('success-soft',
          '',
          'Документ <b>' + document.document_type + '</b> успішно підписано.' ,
          'top-end',
          0,
          true
      )
    },

    onSignedAll() {
      $.SOW.core.toast.show('success-soft',
          '',
          'Усі документи успішно підписано. Ви можете закрити вікно підписання та продовжити роботу.' ,
          'top-end',
          0,
          true
      )
      const dTable = window.DTable["table-documents"]
      dTable.ajax.reload(function () {
        $.SOW.core.ajax_modal.init('.js-ajax-modal')
      })
      this.needsSign = false
    },
  }
}
</script>

<style scoped>

</style>
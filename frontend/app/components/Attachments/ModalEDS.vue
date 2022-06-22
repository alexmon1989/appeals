<template>
  <div class="modal fade"
       id="exampleModalLg"
       tabindex="-1"
       role="dialog"
       aria-labelledby="exampleModalLabelLg"
       aria-hidden="true">
    <div class="modal-dialog modal-lg" role="document">
      <div class="modal-content">

        <div class="modal-header">
          <h5 class="modal-title" id="exampleModalLabelLg">Підписання файлів за допомогою КЕП</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <div class="modal-body mb-3">
          <div v-if="isKeyReaded">
            <spinner v-if="processed"></spinner>
            <table class="table">
              <thead>
              <tr>
                <th scope="col">#</th>
                <th scope="col">Тип (назва) документу</th>
                <th scope="col" class="text-nowrap text-center">Підписано КЕП</th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="(document, index) in documents">
                <th scope="row" v-html="index + 1"></th>
                <td>{{ document.document_type }}</td>
                <td class="fw-bold text-center">
                  <span class="text-success" v-if=" document.sign__count">так</span><span class="text-danger" v-else>ні</span>
                </td>
              </tr>
              </tbody>
            </table>

            <div class="d-flex justify-content-center">
              <button class="btn btn-primary" @click="signFiles" :disabled="processed || !needsSign">
                <svg width="16px" height="16px" xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-pen-fill" viewBox="0 0 16 16">
                  <path d="m13.498.795.149-.149a1.207 1.207 0 1 1 1.707 1.708l-.149.148a1.5 1.5 0 0 1-.059 2.059L4.854 14.854a.5.5 0 0 1-.233.131l-4 1a.5.5 0 0 1-.606-.606l1-4a.5.5 0 0 1 .131-.232l9.642-9.642a.5.5 0 0 0-.642.056L6.854 4.854a.5.5 0 1 1-.708-.708L9.44.854A1.5 1.5 0 0 1 11.5.796a1.5 1.5 0 0 1 1.998-.001z"></path>
                </svg>
                <span class="ms-1">Підписати КЕП</span>
              </button>
            </div>
          </div>
          <div v-else>
            <p>Для продовження роботи, будь ласка, зчитайте ваш ключ:</p>
            <div class="p-4 card rounded-xl">
              <EdsRead @eds-readed="onEDSReaded"></EdsRead>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">
            <i class="fi fi-close"></i>
            Закрити
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>

import Spinner from '../Spinner.vue'
import EdsRead from "../AuthForm/EdsRead.vue"
import { getFileUint8Array, uploadSign } from "../../lib/until"

export default {
  name: "ModalEDS",

  props: {
    'documentsInit': Array,
  },

  components: {
    Spinner,
    EdsRead,
  },

  data () {
    return {
      documents: [],
      processed: false,
      isKeyReaded: false
    }
  },

  watch: {
    documentsInit() {
      this.documents = this.documentsInit.filter(item => item.sign__count === 0)
    }
  },

  methods: {
    onEDSReaded() {
      this.isKeyReaded = true
      $.SOW.core.toast.show('success-soft',
          '',
          'Ключ успішно прочитано. Ви можете підписати файли.',
          'top-end',
          0,
          true
      )
    },

    async getSignInfo(fileData, signData) {
      // Повертає дані про підпис
      const euSign = this.$root.euSign || this.$root.euSignFile

      let info = await euSign.VerifyAsync(fileData, signData)

      const ownerInfo = info.ownerInfo
      const timeInfo = info.timeInfo

      const res = {}
      res['subject'] = ownerInfo.subjCN
      res['issuer'] = ownerInfo.issuerCN
      res['serial'] = ownerInfo.serial
      res['timestamp'] =  "Мітка часу (від даних): " + timeInfo.time

      return res
    },

    async signFiles() {
      this.processed = true
      const euSign = this.$root.euSign || this.$root.euSignFile // Бібліотека для апаратного чи файлового ключа

      let error = null
      for (let i = 0; i < this.documents.length; i++) {
        try {
          // Получение содержимого фала
          let data = await getFileUint8Array(this.documents[i].file_url)

          // Подписание файла
          let eds = await euSign.SignAsync(data)
          // eds = Uint8Array.from(atob(eds), c => c.charCodeAt(0))
          console.log(eds)

          // Данные подписи
          const signInfo = await this.getSignInfo(data, eds)
          console.log(signInfo)

          // Отправка данных на сервер
          const uploadedRes = await uploadSign(this.documents[i].id, eds, signInfo)
          console.log(uploadedRes)

          this.$emit('signedDoc', {'id': this.documents[i].id, 'eds': eds})
        } catch (err) {
          error = err
          console.log(error)
        }
      }

      if (!error) {
        this.$emit('signedAll')
      }

      this.processed = false
    }
  },

  computed: {
    needsSign() {
      const noSign = (document) => document.sign__count === 0
      return this.documents.some(noSign)
    }
  },
}
</script>

<style scoped>

</style>
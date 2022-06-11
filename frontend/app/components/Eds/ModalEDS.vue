<template>
  <b-modal ref="modal" size="lg" hide-footer @hidden="hideModal()" title="Підписання файлів">
    <div v-if="isKeyReaded">
      <table class="table">
        <tr>
          <th scope="col">Ім'я файлу</th>
          <th scope="col">Розмір</th>
        </tr>
        <tr v-for="file in filesForSign" :key="file.guid">
          <td>{{ file.originalName }}</td>
          <td>{{ file.size }}</td>
        </tr>
      </table>
      <b-button variant="primary" @click="sign">
        Підписати
      </b-button>
    </div>
    <EdsRead v-else @eds-readed="isKeyReaded = true" />
    <Spinner :show="processed" />
  </b-modal>
</template>

<script>
  import functions from '../Opiv/functions'
  import Spinner from '../Spinner'
  import EdsRead from './EdsRead'
  export default {
    name: 'ModalEDS',
    components: {
      EdsRead, Spinner
    },
    props: {
      show: {
        type: Boolean,
        default: false
      },
      hideModal: {
        type: Function,
        default: () => {}
      },
      files: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        processed: false,
        isKeyReaded: false
      }
    },
    computed: {
      filesForSign () {
        return this.files.filter(i => !i.eds)
      }
    },
    watch: {
      show (val) {
        if (val) {
          this.$refs.modal.show()
        } else {
          this.$refs.modal.hide()
        }
      }
    },
    methods: {
      async sign () {
        const euSign = this.$root.euSign || this.$root.euSignFile // Бібліотека для апаратного чи файлового ключа
        const filesForSign = this.files.filter(i => !i.eds)
        const signed = []
        let error = null
        this.$nuxt.$loading.start()
        this.processed = true
        for await (const file of filesForSign) {
          try {
            const data = await functions.getFile(file)
            const copy = { ...file }
            copy.eds = await euSign.SignAsync(data)
            signed.push(copy)
          } catch (err) {
            console.log(err)
            error = err
            this.processed = false
            break
          }
        }
        this.processed = false
        this.$nuxt.$loading.finish()
        this.$emit('eds', error, signed)
      }
    }
  }
</script>

<style scoped>

</style>

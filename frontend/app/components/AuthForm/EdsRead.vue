<template>
  <div class="p-4 p-md-5 card rounded-xl">

    <ul class="nav nav-lg nav-pills nav-fill mb-4" id="myTab">
      <li class="nav-item" role="presentation">
        <a class="nav-link active" id="home-tab" data-bs-toggle="tab" href="#file-form" role="tab">Файловий ключ</a>
      </li>
      <li class="nav-item" role="presentation">
        <a class="nav-link" id="profile-tab" data-bs-toggle="tab" href="#hardware-form" role="tab">Апаратний ключ</a>
      </li>
    </ul>

    <div class="tab-content" id="myTabContent">
      <div class="tab-pane fade show active" id="file-form" role="tabpanel">
         <FileKeyContent
          :active-tab="activeTab"
          :errors="errors"
          :acsk-options="acskOptions"
          :processed="processed"
          @update="updateFileKey"
          @read-key="readFileKeyHandler"
        />
      </div>
      <div class="tab-pane fade" id="hardware-form" role="tabpanel">
        Не готове
      </div>
    </div>

  </div>
</template>

<script>
  import CAs from "@/app/lib/ds/eus/CAs"
  import { EUSInit } from './EUSignConfig'
  import { EUSWorkerInit } from '@/app/lib/ds/js/eus-init'
  import FileKeyContent from './FileKeyContent.vue'

  export default {
    name: 'EdsRead',
    components: {
      FileKeyContent,
    },
    data () {
      return {
        isEusInit: false,
        activeTab: 0,
        agreement: false,
        password: '',
        fileKey: null,
        errors: [],
        agreementState: false,
        keyInfo: null,
        alerts: [],
        acskOptions: [],
        cmpFileKeyServers: null,
        cmpHardwareServers: null,
        processed: false,
        type: null,
        device: null
      }
    },
    computed: {
      isKeyReaded () {
        return this.keyInfo && this.agreement
      }
    },
    async mounted () {
      try {
        this.processed = true
        this.$root.euSignFile = await EUSWorkerInit()
        this.acskOptions = [{ selectAll: true, issuerCNs: ["Визначити автоматично"]}, ...CAs]
      } catch (err) {
        console.log(err)
      } finally {
        this.processed = false
      }
    },
    methods: {
      async eusInit() {
        try {
          this.processed = true
          this.$root.euSign = await EUSInit()
          this.isEusInit = true;
        } catch (err) {
          console.log(err)
          throw err;
        } finally {
          this.processed = false
        }
      },

      updateFileKey ({ password, fileKey, acskSelected }) {
        this.password = password
        this.fileKey = fileKey
        this.cmpFileKeyServers = acskSelected.selectAll
          ? this.acskOptions.filter(server => !server.selectAll).map(server => `${server.cmpAddress}`)
          : [`${acskSelected.cmpAddress}`]
      },

      async readFileKeyHandler () {
        try {
          const euSign = this.$root.euSignFile
          this.processed = true
          this.errors = []
          const keyInfo = await euSign.GetKeyInfoBinary(this.fileKey, this.password)
          const cmps = this.cmpFileKeyServers.map(server => `${server}`);
          const cert = await euSign.GetCertificatesByKeyInfo(keyInfo, cmps)
          await euSign.SaveCertificates(cert)
          // this.makeAlert('Ключ успішно завантажено', 'success')
          await euSign.ReadPrivateKeyBinary(this.fileKey, this.password)
          this.keyInfo = await euSign.GetPrivateKeyOwnerInfo()
          this.$root.keyInfo = this.keyInfo
          this.$emit('eds-readed')
        } catch (err) {
          console.log(err)
          const { errorCode, message } = err
          this.errors.push({ errorCode, message })
        } finally {
          this.processed = false
        }
      },
    }
  }
</script>

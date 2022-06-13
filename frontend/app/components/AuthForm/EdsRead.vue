<template>
  <div>
    <ul class="nav nav-lg nav-pills nav-fill mb-5" id="myTab">
      <li class="nav-item" role="presentation">
        <a class="nav-link active fs-5"
           id="home-tab"
           data-bs-toggle="tab"
           href="#file-form"
           role="tab"
           @click="activateTab(0)">Файловий ключ</a>
      </li>
      <li class="nav-item" role="presentation">
        <a class="nav-link fs-5"
           id="profile-tab"
           data-bs-toggle="tab"
           href="#hardware-form"
           @click="activateTab(1)"
           role="tab">Токен</a>
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
        <HardwareKeyContent
          :is-eus-init="isEusInit"
          :active-tab="activeTab"
          :acsk-options="acskOptions"
          :errors="errors"
          :processed="processed"
          @setProcessed="setProcessed"
          @update="updateHardwareKey"
          @read-key="readHardwareKeyHandler"
        />
      </div>
    </div>

  </div>
</template>

<script>
  import CAs from "@/app/lib/ds/eus/CAs"
  import { EUSInit } from './EUSignConfig'
  import { EUSWorkerInit } from '@/app/lib/ds/js/eus-init'
  import FileKeyContent from './FileKeyContent.vue'
  import HardwareKeyContent from './HardwareKeyContent.vue'

  export default {
    name: 'EdsRead',
    components: {
      FileKeyContent,
      HardwareKeyContent,
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
        this.password = ''
        $.SOW.core.toast.destroy()
      }
    },
    methods: {
      async activateTab (tab) {
        this.$emit('tab-change')
        this.errors = []
        this.password = ''
        this.activeTab = tab
        this.keyInfo = null
        if (tab === 1 && !this.$root.euSign) {
          await this.eusInit();
        }
      },

      async eusInit() {
        try {
          this.processed = true
          this.$root.euSign = await EUSInit()
          this.isEusInit = true;
        } catch (err) {
          // console.log(err)
          this.errors.push({
            'errorCode': '',
            'message': err
          })
          // throw err;
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

      updateHardwareKey ({type, device, password, acskSelected}) {
        this.password = password
        this.type = type
        this.device = device
        this.cmpHardwareServers = acskSelected.selectAll
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

      async readHardwareKeyHandler () {
        const euSign = this.$root.euSign
        this.processed = true
        try {
          this.errors = []
          const { password, type, device } = this
          const { typeIndex, devIndex } = this.device
          const keyInfo = await euSign.GetKeyInfoSilentlyAsync(typeIndex, devIndex, this.password)
          const cert = await euSign.GetCertificatesByKeyInfoAsync(keyInfo, this.cmpHardwareServers, this.cmpHardwareServers.map(server => '80'))
          await euSign.SaveCertificatesAsync(cert)
          const privateKey = await euSign.ReadPrivateKeySilentlyAsync(typeIndex, devIndex, this.password)
          this.keyInfo = await euSign.GetPrivateKeyOwnerInfoAsync()
          console.log('keyInfo: ', this.keyInfo);
          const { subjCN, issuerCN, serial } = this.keyInfo
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

      setProcessed (value) {
        this.processed = !!value
      },
    }
  }
</script>

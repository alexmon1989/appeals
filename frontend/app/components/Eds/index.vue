<template>
  <div class="eds-widget">
    <b-tabs content-class="mt-3" @activate-tab="activateTab">
      <b-tab title="Файловий носій" active>
        <FileKeyContent
          :active-tab="activeTab"
          :errors="errors"
          :acsk-options="acskOptions"
          @update="updateFileKey"
          @read-key="readFileKeyHandler"
        />
      </b-tab>
      <b-tab title="Захищений носій">
        <HardwareKeyContent
          :set-processed="setProcessed"
          :is-eus-init="isEusInit"
          :active-tab="activeTab"
          :acsk-options="acskOptions"
          :errors="errors"
          @update="updateHardwareKey"
          @read-key="readHardwareKeyHandler"
        />
      </b-tab>
    </b-tabs>
    <Alerts :alerts="alerts" />
    <b-form-checkbox
      v-model="agreement"
      name="personal-data"
      class="personal-data"
      :state="agreementError ? !agreementError : undefined"
      @update="updateHardwareKey"
    >
      Даю згоду на передачу та обробку персональних даних
    </b-form-checkbox>
    <div class="personal-data-btns">
      <b-button variant="primary" :disabled="!isKeyReaded" @click="proceed">
        Продовжити
      </b-button>
      <b-button variant="light" @click="cancelBtnHandler">
        Скасувати
      </b-button>
    </div>
    <Spinner :show="processed" />
  </div>
</template>

<script>
  /* eslint-disable */
  import { mapActions } from 'vuex'
  import CAs from './CAs.json';
  import Spinner from '../../components/Spinner'
  import { EUSInit } from './EUSignConfig'
  import { EUSWorkerInit } from '../../static/js/eus-init'
  import { randomString } from '../../until'
  import FileKeyContent from './FileKeyContent'
  import HardwareKeyContent from './HardwareKeyContent'
  import Alerts from './Alerts'
  import { fileKeyValidator, hardwareKeyValidator } from './validation'
  import { ownerInfo, errorAlert, errorAlert4097 } from './alertTemplates'

  export default {
    name: 'Eds',
    props: {
      cancelBtnHandler: {
        type: Function,
        default: () => {}
      }
    },
    components: {
      FileKeyContent,
      HardwareKeyContent,
      Alerts,
      Spinner
    },
    data () {
      return {
        isEusInit: false,
        isEusFileInit: false,
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
    head: {
      title: 'Авторизація КЕП',
    },
    computed: {
      agreementError () {
        return this.errors.find(item => item.context.key === 'agreement')?.message
      },
      isKeyReaded () {
        return this.keyInfo && this.agreement
      }
    },
    async mounted () {
      if (this.isEusFileInit) {
        return false;
      }
      try {
        this.processed = true
        this.$root.euSignFile = await EUSWorkerInit()
        this.acskOptions = [{ selectAll: true, issuerCNs: ["Визначити автоматично"]}, ...CAs]
        this.isEusFileInit = true;
        console.log('T: ', this.$root.euSignFile);
      } catch (err) {
        console.log(err)
      } finally {
        this.processed = false
      }
    },
    methods: {
      ...mapActions({
        LOGIN: 'user/LOGIN'
      }),
      async eusInit() {
        if (this.isEusInit) {
          return false;
        }
        try {
          this.processed = true
          this.$root.euSign = await EUSInit()
          this.isEusInit = true;
        } catch (err) {
          this.clearAlerts()
          this.makeAlert(err, 'danger')
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
      async activateTab (tab) {
        console.log('tab: ', tab)
        this.clearAlerts()
        this.errors = []
        this.password = ''
        this.activeTab = tab
        this.keyInfo = null
        if (tab === 1 && !this.$root.euSign) {
          await this.eusInit();
        }
      },
      proceed () {
        if (this.agreement) {
          this.LOGIN(this.keyInfo)
        } else {
          this.$bvToast.toast('Заповніть обов\'язкові поля', {
            autoHideDelay: 4000,
            headerClass: 'd-none',
            variant: 'danger'
          })
        }
      },
      async fileKeyHandler () {
        try {
          const { password, fileKey, agreement } = this
          // Валідація
          await fileKeyValidator({ password, fileKey, agreement })
          this.errors = []
        } catch (errors) {
          this.errors = errors
        }
      },
      async hardwareKeyHandler () {
        try {
          const euSign = this.$root.euSign
          const { type, device, password } = this
          await hardwareKeyValidator({ type, device, password })
          this.errors = []
        } catch (errors) {
          this.errors = errors
        }
      },
      async readHardwareKeyHandler () {
        try {
          if (!this.$root.euSign) {
            await this.eusInit();
          }
          const euSign = this.$root.euSign
          this.processed = true
          this.clearAlerts()
          this.errors = []
          const { password, type, device } = this
          const validation = await hardwareKeyValidator({password, type, device})
          if (validation.error) {
            this.errors = validation.error.details
            return false
          }
          const { typeIndex, devIndex } = this.device
          const keyInfo = await euSign.GetKeyInfoSilentlyAsync(typeIndex, devIndex, this.password)
          const keyInfoArr = Array.from(keyInfo)
          const cert = await euSign.GetCertificatesByKeyInfoAsync(keyInfo, this.cmpHardwareServers, this.cmpHardwareServers.map(server => '80'))
          await euSign.SaveCertificatesAsync(cert)
          this.makeAlert('Ключ успішно завантажено', 'success')
          const privateKey = await euSign.ReadPrivateKeySilentlyAsync(typeIndex, devIndex, this.password)
          this.keyInfo = await euSign.GetPrivateKeyOwnerInfoAsync()
          this.keyInfo = {...this.keyInfo, keyInfoArr}
          const { subjCN, issuerCN, serial } = this.keyInfo
          this.makeAlert(ownerInfo(subjCN, issuerCN, serial), 'success')
          this.$root.keyInfo = this.keyInfo
        } catch (err) {
          const { errorCode, message } = err
          this.makeAlert(errorAlert(errorCode, message), 'danger')
          console.log(err)
        } finally {
          this.processed = false
        }
      },
      async readFileKeyHandler () {
        try {
          const euSign = this.$root.euSignFile
          this.processed = true
          this.clearAlerts()
          this.errors = []
          const { password, fileKey } = this
          const validation = await fileKeyValidator({ password, fileKey })
          if (validation.error) {
            this.errors = validation.error.details
            return false
          }
          const keyInfo = await euSign.GetKeyInfoBinary(this.fileKey, this.password)
          const keyInfoArr = Array.from(keyInfo)
          const cmps = this.cmpFileKeyServers.map(server => `${server}`);
          const cert = await euSign.GetCertificatesByKeyInfo(keyInfo, cmps)
          await euSign.SaveCertificates(cert)
          this.makeAlert('Ключ успішно завантажено', 'success')
          await euSign.ReadPrivateKeyBinary(this.fileKey, this.password)
          this.keyInfo = await euSign.GetPrivateKeyOwnerInfo()
          this.keyInfo = {...this.keyInfo, keyInfoArr}
          const { subjCN, issuerCN, serial } = this.keyInfo
          this.makeAlert(ownerInfo(subjCN, issuerCN, serial), 'success')
          this.$root.keyInfo = this.keyInfo
        } catch (err) {
          const { errorCode, message } = err
          this.makeAlert(errorAlert(errorCode, message), 'danger')
        } finally {
          this.processed = false
        }
      },
      makeAlert (html, variant = 'primary') {
        this.alerts.push({ html, variant, id: randomString() })
      },
      clearAlerts () {
        this.alerts = []
      },
      setProcessed (value) {
        this.processed = value
      },
    }
  }
</script>

<style lang="scss" scoped>
  .personal-data {
    margin-bottom: 20px;
  }
  .eds-widget {
    position: relative;
  }
</style>

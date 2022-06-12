<template>
  <Form @submit="readHandler">
    <spinner v-if="processed"></spinner>

    <div class="alert alert-danger alert-dismissible border-1 fade show" role="alert" v-if="errors.length > 0">
      <ul class="list-unstyled mb-0">
        <li v-for="error in errors" v-html="showError(error)"></li>
      </ul>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>

    <div class="mb-3">
      <label for="hw_type" class="form-label fw-bold">Тип носія</label>
      <Field name="hw_type"
             rules="required"
             label="Тип носія"
             v-model="selectedDeviceType"
             v-slot="{ handleChange, handleBlur, meta }">
        <select id="hw_type"
                class="form-select"
                @change="handleChange"
                @blur="handleBlur"
                :class="{ 'is-invalid': !meta.valid && meta.touched }"
                :disabled="!isEusInit"
                @input="updateEmit">
          <option v-for="type in types"
                  :value="type"
                  :selected="selectedDeviceType && type.value === selectedDeviceType.value"
          >{{ type.value }}</option>
        </select>
      </Field>
      <ErrorMessage name="hw_type" class="invalid-feedback" />
    </div>

    <div class="mb-3">
      <label for="hw_device" class="form-label fw-bold">Назва носія</label>
      <Field name="hw_device"
             rules="required"
             label="Назва носія"
             v-model="selectedDevice"
             v-slot="{ handleChange, handleBlur, meta }">
        <select id="hw_device"
                class="form-select"
                @change="handleChange"
                @blur="handleBlur"
                :class="{ 'is-invalid': !meta.valid && meta.touched }"
                :disabled="!isEusInit"
                @input="updateEmit">
          <option v-for="deviceItem in deviceItems"
                  :selected="selectedDevice && deviceItem.uniqueId === selectedDevice.uniqueId"
                  :value="deviceItem">{{ deviceItem.device }}</option>
        </select>
      </Field>
      <ErrorMessage name="hw_device" class="invalid-feedback" />
    </div>

    <div class="mb-3">
      <label for="acsk_hw" class="form-label fw-bold">Оберіть АЦСК</label>
      <Field name="acsk_hw"
             rules="required"
             label="Оберіть АЦСК"
             v-model="acskSelected"
             v-slot="{ handleChange, handleBlur, meta }">
        <select id="acsk_hw"
                class="form-select"
                @change="handleChange"
                @blur="handleBlur"
                :class="{ 'is-invalid': !meta.valid && meta.touched }"
                :disabled="!isEusInit"
                @input="updateEmit">
          <option v-for="acsk in acskOptions"
                  :value="acsk">{{ acskLabel(acsk) }}</option>
        </select>
      </Field>
      <ErrorMessage name="acsk_hw" class="invalid-feedback" />
    </div>

    <div class="mb-3">
      <label for="password_hw" class="form-label fw-bold">Пароль</label>
      <Field name="password_hw"
             v-model="password"
             rules="required"
             label="Пароль"
             v-slot="{ field, meta }">
        <input type="password"
               v-bind="field"
               id="password_hw"
               class="form-control"
               :class="{ 'is-invalid': !meta.valid && meta.touched }"
               :disabled="!isEusInit"
               @input="updateEmit"
        />
      </Field>
      <ErrorMessage name="password_hw" class="invalid-feedback" />
    </div>

    <div class="row">
      <div class="col-12 mt-1">
        <button type="submit"
                :disabled="processed || !isEusInit"
                class="btn btn-primary w-100 fw-medium"
        >Зчитати</button>
      </div>
    </div>
  </Form>
</template>

<script>
import { Form, Field, ErrorMessage } from 'vee-validate'
import Spinner from "../Spinner.vue"

export default {
  name: 'HardwareKeyContent',
  components: {
    Form,
    Field,
    ErrorMessage,
    Spinner,
  },
  props: {
    acskOptions: {
      type: Array,
      default: () => ([])
    },
    activeTab: {
      type: Number,
      default: () => 0
    },
    isEusInit: {
      type: Boolean,
      default: () => false
    },
    errors: {
      type: Array,
      default: () => ([])
    },
    processed: {
      type: Boolean
    }
  },
  data () {
    return {
      deviceTypes: [],
      devices: [],
      selectedDeviceType: null,
      selectedDevice: null,
      acskSelected: "",
      password: '',
    }
  },
  computed: {
    types () {
      return this.deviceTypes.reduce((acc, type) => {
        acc.push({
          key: type.index,
          typeIndex: type.index,
          value: type.title,
          $isDisabled: !this.hasDevice(type.index, this.devices)
        })
        return acc
      }, [{ key: 'ALL', value: 'Відобразити ключі для всіх типів', $isDisabled: false }])
      .sort((a, b) => {
        if (a.$isDisabled > b.$isDisabled) {
          return 1
        }
        if (a.$isDisabled < b.$isDisabled) {
          return -1
        }
        return 0
      })
    },
    deviceItems () {
      if (this.selectedDeviceType && this.selectedDeviceType.key !== 'ALL') {
        return this.devices.filter(device => device.typeIndex === this.selectedDeviceType.key)
      } else {
        return this.devices
      }
    },
    typeError () {
      return this.errors.find(item => item.context.key === 'type')?.message
    },
    deviceError () {
      return this.errors.find(item => item.context.key === 'device')?.message
    },
    passError () {
      return this.errors.find(item => item.context.key === 'password')?.message
    }
  },
  watch: {
    acskOptions (values) {
      this.acskSelected = values[0]
      this.updateEmit()
    },
    activeTab () {
      this.password = ''
    },
    async isEusInit () {
      try {
        this.$emit('setProcessed', true)
        // this.processed = true
        this.deviceTypes = await this.$root.euSign.AsyncGetKeyMediaTypes()
        this.devices = await this.$root.euSign.getAllKeys(this.deviceTypes)
      } catch (err) {
        /* eslint-disable no-console */
        console.log(err)
        /* eslint-enable no-console */
      } finally {
        this.$emit('setProcessed', false)
        // this.processed = false
      }
      this.setAuto()
    }
  },
  methods: {
    readHandler () {
      this.$emit('read-key')
    },
    hasDevice (typeIndex) {
      if (typeIndex === 'ALL') {
        return true
      }
      return this.devices.some(device => device.typeIndex === typeIndex)
    },
    acskLabel ({ issuerCNs }) {
      return issuerCNs[0]
    },
    updateEmit () {
      this.$emit('update', {
        type: this.selectedDeviceType,
        device: this.selectedDevice,
        password: this.password,
        acskSelected: this.acskSelected
      })
    },
    setAuto () {
      if (!this.devices.length) {
        return false
      }
      const { typeIndex } = this.devices[0]
      this.selectedDeviceType = this.types.find(type => type.typeIndex === typeIndex)
      this.selectedDevice = this.devices[0]
    },
    showError(error) {
      let res = ''
      if (error.errorCode) {
        res = error.errorCode + ':&nbsp;'
      }
      return res + error.message
    }
  }
}
</script>


<template>
  <div class="form-wrap">
    <b-form-group label-cols="2" label-cols-lg="2" label-size="sm" label="Тип носія" label-for="input-sm">
      <multiselect
        v-model="selectedDeviceType"
        label="value"
        track-by="key"
        group-label="key"
        placeholder="Оберіть тип носія"
        :class="{'danger': typeError}"
        :options="types"
        :searchable="true"
        :hide-selected="true"
        @input="updateEmit"
      >
        <template slot="noResult">
          Не знайдено носія такого типу
        </template>
        <template slot="noOptions">
          Немає доступних носіїв
        </template>
      </multiselect>
      <b-form-invalid-feedback :state="!typeError">
        {{ typeError }}
      </b-form-invalid-feedback>
    </b-form-group>
    <b-form-group label-cols="2" label-cols-lg="2" label-size="sm" label="Назва носія" label-for="input-sm">
      <multiselect
        v-model="selectedDevice"
        label="device"
        placeholder="Оберіть носій"
        :class="{'danger': deviceError}"
        :options="deviceItems"
        :searchable="false"
        :hide-selected="true"
        @input="updateEmit"
      >
        <template slot="noResult">
          Не знайдено носія такого типу
        </template>
        <template slot="noOptions">
          Немає доступних носіїв
        </template>
      </multiselect>
      <b-form-invalid-feedback :state="!deviceError">
        {{ deviceError }}
      </b-form-invalid-feedback>
    </b-form-group>
    <b-form-group label-cols="2" label-cols-lg="2" label-size="sm" label="Оберіть АЦСК" label-for="input-sm">
      <multiselect
        v-model="acskSelected"
        placeholder="Оберіть АЦСК"
        :allow-empty="false"
        :options="acskOptions"
        :searchable="false"
        :hide-selected="true"
        :custom-label="acskLabel"
        @input="updateEmit"
      />
    </b-form-group>
    <b-form-group label-cols="2" label-cols-lg="2" label-size="sm" label="Пароль" label-for="input-sm">
      <b-input-group size="sm">
        <b-form-input
          v-model="password"
          type="password"
          :state="passError ? !passError : undefined"
          placeholder="Введіть пароль"
          @input="updateEmit"
        />
        <b-input-group-append>
          <b-button size="sm" text="Button" variant="primary" class="read-pass" @click="readHandler">
            Зчитати
          </b-button>
        </b-input-group-append>
        <b-form-invalid-feedback :state="!passError">
          {{ passError }}
        </b-form-invalid-feedback>
      </b-input-group>
    </b-form-group>
    <Spinner :show="processed" />
  </div>
</template>

<script>
import Spinner from '../../components/Spinner'

export default {
  name: 'HardwareKeyContent',
  components: {
    Spinner
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
    }
  },
  data () {
    return {
      processed: false,
      deviceTypes: [],
      devices: [],
      selectedDeviceType: null,
      selectedDevice: null,
      acskSelected: null,
      password: ''
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
        this.processed = true
        this.deviceTypes = await this.$root.euSign.AsyncGetKeyMediaTypes()
        this.devices = await this.$root.euSign.getAllKeys(this.deviceTypes)
      } catch (err) {
        /* eslint-disable no-console */
        console.log(err)
        /* eslint-enable no-console */
      } finally {
        this.processed = false
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
    }
  }
}
</script>

<style lang="scss" scoped>
  .form-wrap {
    padding-top: 15px;
  }
  .form-group {
    margin-bottom: 1.2rem;
  }
</style>

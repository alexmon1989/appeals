<template>
  <div class="form-wrap">
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
    <b-form-group label-cols="2" label-cols-lg="2" label-size="sm" label="Ключ" label-for="input-sm">
      <b-form-file
        ref="file-input"
        placeholder="Виберіть файл, або перетягніть сюди..."
        drop-placeholder="Drop file here..."
        browse-text="Обрати"
        size="sm"
        :state="keyError ? !keyError : undefined"
        @change="readKey"
      />
      <b-form-invalid-feedback :state="!keyError">
        {{ keyError }}
      </b-form-invalid-feedback>
    </b-form-group>
    <b-form-group label-cols="2" label-cols-lg="2" label-size="sm" label="Пароль" label-for="input-sm">
      <b-input-group size="sm">
        <b-form-input
          v-model="password"
          type="password"
          placeholder="Введіть пароль"
          :state="passError ? !passError : undefined"
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
  </div>
</template>

<script>
  export default {
  name: 'FileKeyContent',
  props: {
    acskOptions: {
      type: Array,
      default: () => ([])
    },
    errors: {
      type: Array,
      default: () => ([])
    },
    activeTab: {
      type: Number,
      default: () => 0
    }
  },
  data () {
    return {
      acskSelected: null,
      password: '',
      fileKey: null
    }
  },
  computed: {
    keyError () {
      return this.errors.find(item => item.context.key === 'fileKey')?.message
    },
    passError () {
      return this.errors.find(item => item.context.key === 'password')?.message
    }
  },
  watch: {
    acskOptions (values) {
      this.acskSelected = values[0]
      this.updateEmit()
    }
  },
  methods: {
    readKey (event) {
      const self = this
      const reader = new FileReader()
      reader.onload = function () {
        const arrayBuffer = this.result
        self.fileKey = new Uint8Array(arrayBuffer)
        self.updateEmit()
      }
      reader.readAsArrayBuffer(event.target.files[0])
    },
    updateEmit () {
      const { password, fileKey, acskSelected } = this
      this.$emit('update', {
        password,
        fileKey,
        acskSelected
      })
    },
    readHandler () {
      this.$emit('read-key')
    },
    acskLabel ({ issuerCNs }) {
      return issuerCNs[0]
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
  .read-pass {
    min-width: 91px;
    text-align: center;
  }
</style>

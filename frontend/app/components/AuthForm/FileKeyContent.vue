<template>
  <Form @submit="readHandler">
    <div class="alert alert-danger alert-dismissible border-1 fade show" role="alert" v-if="errors.length > 0">
      <ul class="list-unstyled mb-0">
        <li v-for="error in errors">
          <span v-if="error.errorCode">{{ error.errorCode }}:&nbsp;</span>{{ error.message }}
        </li>
      </ul>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>

    <div class="mb-3">
      <label for="acsk_file" class="form-label fw-bold">Оберіть АЦСК</label>
      <Field name="acsk_file"
             rules="required"
             label="Оберіть АЦСК"
             v-slot="{ handleChange, handleBlur, meta }">
        <select id="acsk_file"
                class="form-select"
                v-model="acskSelected"
                @change="handleChange"
                @blur="handleBlur"
                :class="{ 'is-invalid': !meta.valid && meta.touched }"
                @input="updateEmit">
          <option v-for="acsk in acskOptions" :value="acsk">{{ acskLabel(acsk) }}</option>
        </select>
      </Field>
      <ErrorMessage name="acsk_file" class="invalid-feedback" />
    </div>

    <div class="mb-3">
      <label for="file" class="form-label fw-bold">Ключ</label>
      <Field name="file"
             rules="required"
             label="Ключ"
             v-slot="{ handleChange, handleBlur, meta }">
        <input type="file"
               id="file"
               class="form-control"
               :class="{ 'is-invalid': !meta.valid && meta.touched }"
               @change="handleChange"
               @blur="handleBlur"
               @input="readKey"
        />
      </Field>
      <ErrorMessage name="file" class="invalid-feedback" />
    </div>

    <div class="mb-3">
      <label for="password_file" class="form-label fw-bold">Пароль</label>
      <Field name="password_file"
             v-model="password"
             rules="required"
             label="Пароль"
             v-slot="{ field, meta }">
        <input type="password"
               v-bind="field"
               id="password_file"
               class="form-control"
               :class="{ 'is-invalid': !meta.valid && meta.touched }"
               @input="updateEmit"
        />
      </Field>
      <ErrorMessage name="password_file" class="invalid-feedback" />
    </div>

    <div class="row">
      <div class="col-12 mt-1">
        <button type="submit"
                :disabled="processed"
                class="btn btn-primary w-100 fw-medium"
        >Зчитати</button>
      </div>
    </div>

  </Form>
</template>

<script>
  import { Form, Field, ErrorMessage } from 'vee-validate'

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
    processed: {
      type: Boolean
    }
  },
  components: {
    Form, Field, ErrorMessage
  },
  data () {
    return {
      acskSelected: "",
      password: "",
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

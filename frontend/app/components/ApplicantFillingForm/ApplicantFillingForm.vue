<template>
  <div>
    <Form enctype="multipart/form-data" id="app-form" @submit="onSubmit" v-slot="{ meta }">
      <div class="row g-4">
        <div class="col-md">
          <div class="mb-3">
            <label class="form-label fw-medium" for="obj_kind">Об’єкт права інтелектуальної власності</label>
            <Field name="obj_kind"
                   v-model="objKindSelected"
                   rules="required"
                   label="Об’єкт права інтелектуальної власності"
                   v-slot="{ field, meta }">
              <select class="form-select"
                      :class="{ 'is-invalid': !meta.valid && meta.touched }"
                      id="obj_kind"
                      v-bind="field"
              >
                <option value="" disabled>Оберіть тип</option>
                <option v-for="objKind in objKinds" :value="objKind.pk">
                  {{ objKind.title }}
                </option>
              </select>
            </Field>
            <ErrorMessage name="obj_kind" class="invalid-feedback"/>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-md">
          <claim-kind-select v-model="claimKindSelected"
                         :claim-kinds="claimKinds"
                         :obj-kind-id="objKindSelected"
          ></claim-kind-select>
        </div>
      </div>

      <div v-if="stage3Fields.length > 0 || (stage4Fields.length > 0 && dataLoadedSIS)">
        <div class="row g-4">
          <div class="col-md" v-for="field in stage3Fields">
            <claim-field :field-title="field.title"
                         :field-id="field.input_id"
                         :field-type="field.field_type"
                         :field-editable="!!field.editable"
                         :field-required="!!field.required"
                         :field-help-text="field.help_text"
                         v-model="stage3Values[field.input_id]"
            ></claim-field>
          </div>

          <div class="col-md" v-for="field in stage4Fields" v-if="dataLoadedSIS">
            <claim-field :field-title="field.title"
                         :field-id="field.input_id"
                         :field-type="field.field_type"
                         :field-editable="!!field.editable"
                         :field-required="!!field.required"
                         :field-help-text="field.help_text"
                         v-model="stage4Values[field.input_id]"
            ></claim-field>
          </div>
        </div>
      </div>

      <div v-if="processed"
           class="text-primary"
      >Будь ласка, зачекайте, завантажуємо дані об'кта інтелектуальної власності...</div>

      <div class="row g-4" v-if="(stage5Fields.length > 0 || stage6Fields.length > 0) && dataLoadedSIS">
        <div class="col-md" v-if="stage5Fields.length > 0">
          <h2 class="h5 my-3 text-indigo-800" v-if="isApplication">Відомості про заявника:</h2>
          <h2 class="h5 my-3 text-indigo-800" v-else>Відомості про власника:</h2>

          <div class="row">
            <div class="col-12" v-for="field in stage5Fields">
              <claim-field :field-title="field.title"
                           :field-id="field.input_id"
                           :field-type="field.field_type"
                           :field-editable="!!field.editable"
                           :field-required="!!field.required"
                           :field-help-text="field.help_text"
                           v-model="stage5Values[field.input_id]"
              ></claim-field>
            </div>
          </div>
        </div>

        <div class="col-md" v-if="stage6Fields.length > 0 && dataLoadedSIS">
            <h2 class="h5 my-3 text-indigo-800">Відомості про апелянта:</h2>

            <div class="col-12" v-for="field in stage6Fields">
              <claim-field :field-title="field.title"
                           :field-id="field.input_id"
                           :field-type="field.field_type"
                           :field-editable="!!field.editable"
                           :field-required="!!field.required"
                           :field-help-text="field.help_text"
                           v-model="stage6Values[field.input_id]"
              ></claim-field>
            </div>
        </div>
      </div>

      <div v-if="stage7Fields.length > 0 && dataLoadedSIS">
        <h2 class="h5 my-3 text-indigo-800">Додаткова інформація</h2>

        <claim-field v-for="field in stage7Fields"
                     :field-title="field.title"
                     :field-id="field.input_id"
                     :field-type="field.field_type"
                     :field-editable="!!field.editable"
                     :field-required="!!field.required"
                     :field-help-text="field.help_text"
                     v-model="stage7Values[field.input_id]"
        ></claim-field>
      </div>

      <div v-if="stage8Fields.length > 0 && dataLoadedSIS">

        <h2 class="h5 my-3 text-indigo-800">Відомості щодо рішення Укрпатенту:</h2>

        <div class="row g-4">
          <div class="col-md" v-for="field in stage8Fields">
            <claim-field :field-title="field.title"
                         :field-id="field.input_id"
                         :field-type="field.field_type"
                         :field-editable="!!field.editable"
                         :field-required="!!field.required"
                         :field-help-text="field.help_text"
                         v-model="stage8Values[field.input_id]"
            ></claim-field>
          </div>
        </div>
      </div>

      <div v-if="stage9Fields.length > 0 && dataLoadedSIS">
        <h2 class="h5 mb-3 mt-4 text-indigo-800">Додатки (файли):</h2>

        <claim-field v-for="field in stage9Fields"
                     :field-title="field.title"
                     :field-id="field.input_id"
                     :field-type="field.field_type"
                     :field-editable="!!field.editable"
                     :field-required="!!field.required"
                     :field-help-text="field.help_text"
                     :field-allowed-extensions="field.allowed_extensions"
                     :initial_documents="getFieldDocuments(field.title)"
                     v-model="stage9Values[field.input_id]"
        ></claim-field>
      </div>

      <div class="alert alert-danger" role="alert" v-if="errors.length > 0">
        <ul class="list-unstyled mb-0">
          <li v-for="error in errors">{{ error }}</li>
        </ul>
      </div>

      <div class="d-flex justify-content-center mb-2">
        <button type="submit"
                :disabled="sending || !dataLoadedSIS"
                class="btn btn-primary mt-4"
        >{{ btnText }}</button>
      </div>
    </form>
  </div>
</template>

<script>
import getDataFromSIS from "@/app/src/sis"
import debounce from "lodash.debounce"
import {ErrorMessage, Field, Form} from 'vee-validate'

import ClaimKindSelect from "./ClaimKindSelect.vue"
import ClaimField from "./ClaimField.vue"
// import ThirdPersonCheckbox from "./ThirdPersonCheckbox.vue"
import Spinner from "../Spinner.vue"
import { getCookie } from '@/app/src/until'

export default {
  components: {
    Form,
    Field,
    ErrorMessage,
    ClaimKindSelect,
    ClaimField,
    Spinner,
    // ThirdPersonCheckbox,
  },

  props: {
    objKinds: Array,
    claimKinds: Array,
    claimFields: Array,
    initialData: Object,
  },

  data() {
    return {
      objKindSelected: '',
      claimKindSelected: '',
      thirdPerson: false,
      thirdPersonDisabled: false,
      stage3Values: {},
      stage4Values: {},
      stage5Values: {},
      stage6Values: {},
      stage7Values: {},
      stage8Values: {},
      stage9Values: {},
      dataLoadedSIS: false,
      errors: [],
      sending: false,
      processed: false,
      initialDataLoading: false,
      documents: false,
    }
  },

  watch: {
    objKindSelected() {
      this.claimKindSelected = ''
    },

    claimKindSelected(claimKindId) {
      this.dataLoadedSIS = false
      this.stage3Values = {}
      this.stage4Values = {}
      this.stage5Values = {}
      this.stage6Values = {}
      this.stage7Values = {}
      this.stage8Values = {}
      this.stage9Values = {}
      this.changeThirdPersonCheckbox(claimKindId);
    },

    stage3Values: {
        handler(...args){
          if (!this.initialDataLoading) {
            this.loadDataFromSIS(...args)
          }
        }, deep: true
    }
  },

  created() {
    this.loadDataFromSIS = debounce(async (newValue, oldValue) => {

      this.processed = true
      this.dataLoadedSIS = false
      this.errors = []

      if (Object.values(newValue)[0]) {
        //try {
        let data = await getDataFromSIS(Object.keys(newValue)[0], Object.values(newValue)[0], this.sisId)
        console.log(data)

        if (Object.keys(data).length === 0) {
          this.errors.push('Опублікованих даних щодо об\'єкта не було знайдено. Подача звернення неможлива.')
        } else {

          // Заполнение полей шагов 4, 5
          this.stage4Fields.forEach(field => {
            this.stage4Values[field['input_id']] = data[field['input_id']]
          })
          this.stage5Fields.forEach(field => {
            this.stage5Values[field['input_id']] = data[field['input_id']]
          })

          this.dataLoadedSIS = true
        }
        //} catch (e) {
        //  this.errors.push('Помилка звернення до API СІС.')
        //}
      }
      this.processed = false
    }, 1000);
  },

  beforeUnmount() {
    this.loadDataFromSIS.cancel();
  },

  mounted() {
    if (this.initialData) {
      this.initialDataLoading = true
      this.objKindSelected = this.initialData.obj_kind_id
      this.$nextTick(() => {
        this.claimKindSelected = this.initialData.claim_kind_id
        this.$nextTick(() => {
          this.dataLoadedSIS = true
          this.initialData.stages_data[3].items.forEach((item) => {
            this.stage3Values[item.id] = item.value
          })

          this.$nextTick(() => {
            this.initialData.stages_data[4].items.forEach((item) => {
              if (item.id.includes('date')) {
                const d = new Date(item.value)
                const year = d.getFullYear()
                const month = `${d.getMonth() + 1}`.padStart(2, "0")
                const day = `${d.getDate()}`.padStart(2, "0")
                this.stage4Values[item.id] = [day, month, year].join(".")
              } else {
                this.stage4Values[item.id] = item.value
              }
            })
            this.initialData.stages_data[5].items.forEach((item) => {
              this.stage5Values[item.id] = item.value
            })
            this.initialData.stages_data[6].items.forEach((item) => {
              this.stage6Values[item.id] = item.value
            })
            this.initialData.stages_data[7].items.forEach((item) => {
              this.stage7Values[item.id] = item.value
            })
            this.initialData.stages_data[8].items.forEach((item) => {
              this.stage8Values[item.id] = item.value
            })

            this.initialDataLoading = false
          })
        })
      })

      this.documents = this.initialData.documents
    }
  },

  methods: {
    // Изменяет значение и возможность редактирования чекбокса ThirdPersonCheckbox
    changeThirdPersonCheckbox(claimKindId) {
       if (claimKindId) {
        const claimKind = this.claimKinds.find(obj => obj.pk === claimKindId)
        if (claimKind.third_person) {
          this.thirdPerson = true
          this.thirdPersonDisabled = true
          return
        }
      }
      this.thirdPerson = false
      this.thirdPersonDisabled = false
    },

    // Отправка данных на сервер
    async onSubmit(values) {
      const form = document.getElementById('app-form')
      const formData = new FormData(form)
      const csrftoken = getCookie('csrftoken')
      formData.append('csrfmiddlewaretoken', csrftoken)
      formData.append('third_person', this.thirdPerson | 0)

      this.sending = true

      let response = await fetch('', {
        method: 'POST',
        body: formData
      });

      let result = await response.json();

      this.sending = false

      location.href = result.claim_url
    },

    // Возвращает список документов поля (если есть начальные данные (редактирование обращения))
    getFieldDocuments(fieldTitle) {
      if (this.initialData && this.initialData.documents !== undefined) {
        return this.initialData.documents.filter(item => item.document_type === fieldTitle)
      }
    },
  },

  computed: {

    // Id выбранного типа объекта в СИС
    sisId() {
      if (this.objKindSelected) {
        return this.objKinds.find(item => this.objKindSelected === item.pk).sis_id
      } else {
        return ''
      }
    },

    // Поля ввода данных на этапе 3
    stage3Fields() {
      if (this.claimKindSelected) {
        return this.claimFields.filter(item => item.claim_kind_id === this.claimKindSelected && item.stage === 3)
      }

      return []
    },

    // Поля ввода данных на этапе 4
    stage4Fields() {
      if (this.claimKindSelected) {
        return this.claimFields.filter(item => item.claim_kind_id === this.claimKindSelected && item.stage === 4)
      }

      return []
    },

    // Поля ввода данных на этапе 5
    stage5Fields() {
      if (this.claimKindSelected) {
        return this.claimFields.filter(item => item.claim_kind_id === this.claimKindSelected && item.stage === 5)
      }

      return []
    },

    // Поля ввода данных на этапе 6
    stage6Fields() {
      if (this.claimKindSelected && this.thirdPerson) {
        return this.claimFields.filter(item => item.claim_kind_id === this.claimKindSelected && item.stage === 6)
      }

      return []
    },

    // Поля ввода данных на этапе 7
    stage7Fields() {
      if (this.claimKindSelected) {
        return this.claimFields.filter(item => item.claim_kind_id === this.claimKindSelected && item.stage === 7)
      }

      return []
    },

    // Поля ввода данных на этапе 8
    stage8Fields() {
      if (this.claimKindSelected) {
        return this.claimFields.filter(item => item.claim_kind_id === this.claimKindSelected && item.stage === 8)
      }

      return []
    },

    // Поля ввода данных на этапе 8
    stage9Fields() {
      if (this.claimKindSelected) {
        return this.claimFields.filter(item => item.claim_kind_id === this.claimKindSelected && item.stage === 9)
      }

      return []
    },

    isApplication() {
      if (this.stage3Fields.length > 0) {
        return this.stage3Fields[0]['input_id'] === 'app_number'
      }
      return false
    },

    btnText() {
      return this.initialData ? 'Зберегти' : 'Сформувати та підписати'
    }
  }
}
</script>

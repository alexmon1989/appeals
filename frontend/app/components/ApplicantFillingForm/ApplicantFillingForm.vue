<template>
  <div>
    <form id="create-app-form">

      <h2 class="h5 mb-3 text-indigo-800">Вид звернення:</h2>

      <div class="row g-4">
        <div class="col-md">
          <div class="form-floating mb-3">
            <select class="form-select form-select-sm"
                    id="obj_kind"
                    v-model="objKindSelected">
              <option value="" disabled>Оберіть тип</option>
              <option v-for="objKind in objKinds" :value="objKind.pk">
                {{ objKind.title }}
              </option>
            </select>
            <label for="obj_kind">Об’єкт права інтелектуальної власності:</label>
          </div>
        </div>
        <div class="col-md">
          <claim-kind-select v-model="claimKindSelected"
                         :claim-kinds="claimKinds"
                         :obj-kind-id="objKindSelected"
          ></claim-kind-select>
        </div>
      </div>

      <third-person-checkbox :disabled="thirdPersonDisabled" v-model="thirdPerson"></third-person-checkbox>

      <div v-if="stage3Fields.length > 0 || (stage4Fields.length > 0 && dataLoadedSIS)">
        <h2 class="h5 my-3 text-indigo-800">Дані об'єкта права інтелектуальної власності:</h2>

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

      <div class="row g-4" v-if="(stage5Fields.length > 0 || stage6Fields.length > 0) && dataLoadedSIS">
        <div class="col-md" v-if="stage5Fields.length > 0">
          <h2 class="h5 my-3 text-indigo-800">Відомості про заявника/власника:</h2>

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
            <h2 class="h5 my-3 text-indigo-800">Відомості про апелянта (третю особу):</h2>

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
        <h2 class="h5 my-3 text-indigo-800">Додатки (файли):</h2>

        <claim-field v-for="field in stage9Fields"
                     :field-title="field.title"
                     :field-id="field.input_id"
                     :field-type="field.field_type"
                     :field-editable="!!field.editable"
                     :field-required="!!field.required"
                     :field-help-text="field.help_text"
                     v-model="stage9Values[field.input_id]"
        ></claim-field>
      </div>

      <div class="alert alert-danger" role="alert" v-if="errors.length > 0">
        <ul class="list-unstyled mb-0">
          <li v-for="error in errors">{{ error }}</li>
        </ul>
      </div>

      <div class="d-flex">
        <button type="submit" class="btn btn-primary mt-4">Сформувати заявку</button>
      </div>
    </form>
  </div>
</template>

<script>
import ClaimKindSelect from "./ClaimKindSelect.vue"
import ThirdPersonCheckbox from "./ThirdPersonCheckbox.vue"
import ClaimField from "./ClaimField.vue"
import getDataFromSIS from "@/app/lib/sis"
import debounce from "lodash.debounce"

export default {
  components: {
    ClaimKindSelect,
    ThirdPersonCheckbox,
    ClaimField,
  },

  props: {
    objKinds: Array,
    claimKinds: Array,
    claimFields: Array,
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
            this.loadDataFromSIS(...args)
        }, deep: true
    }
  },

  created() {
    this.loadDataFromSIS = debounce(async (newValue, oldValue) => {

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
    }, 1000);
  },

  beforeUnmount() {
    this.loadDataFromSIS.cancel();
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
      this.thirdPersonDisabled = false
    },

  },

  computed: {

    // Id выбранного типа объекта в СИС
    sisId() {
      return this.objKinds.find(item => this.objKindSelected === item.pk).sis_id
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
    }
  }
}
</script>

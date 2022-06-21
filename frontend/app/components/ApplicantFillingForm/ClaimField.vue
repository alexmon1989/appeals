<template>
  <div class="mb-3" v-if="fieldType === 'text'">
    <label :for="fieldId" class="form-label fw-medium">{{ fieldTitle }}</label>
    <Field :name="fieldId"
           v-model="modelValue"
           :rules="{'required': fieldRequired}"
           :label="label"
           v-slot="{ field, meta }">
      <input type="text"
             v-bind="field"
             :id="fieldId"
             :readonly="!fieldEditable"
             class="form-control"
             :class="{ 'is-invalid': !meta.valid && meta.touched }"
             :placeholder="fieldTitle"
             @input="$emit('update:modelValue', $event.target.value)"
      />
    </Field>
    <ErrorMessage :name="fieldId" class="invalid-feedback" />
  </div>

  <div class="mb-3" v-else-if="fieldType === 'email'">
    <label :for="fieldId" class="fw-medium form-label">{{ fieldTitle }}</label>
    <Field :name="fieldId"
           v-model="modelValue"
           :rules="{'required': fieldRequired}"
           :label="label"
           v-slot="{ field, meta }">
      <input type="email"
             v-bind="field"
             :id="fieldId"
             :readonly="!fieldEditable"
             class="form-control"
             :class="{ 'is-invalid': !meta.valid && meta.touched }"
             :placeholder="fieldTitle"
             @input="$emit('update:modelValue', $event.target.value)"
      />
    </Field>
    <ErrorMessage :name="fieldId" class="invalid-feedback" />
  </div>

  <div class="mb-3" v-else-if="fieldType === 'date'">
    <label :for="fieldId" class="fw-medium form-label">{{ fieldTitle }}</label>
    <Field :name="fieldId"
           v-model="modelValue"
           :rules="{'required': fieldRequired}"
           :label="label"
           v-slot="{ field, meta }">
      <input type="date"
             v-bind="field"
             :id="fieldId"
             :readonly="!fieldEditable"
             class="form-control"
             :class="{ 'is-invalid': !meta.valid && meta.touched }"
             :placeholder="fieldTitle"
             @input="$emit('update:modelValue', $event.target.value)"
      />
    </Field>
    <ErrorMessage :name="fieldId" class="invalid-feedback" />
  </div>

  <div class="mb-3" v-else-if="fieldType === 'textarea'">
    <label :for="fieldId" class="form-label fw-medium">{{ fieldTitle }}</label>
    <Field :name="fieldId"
           v-model="modelValue"
           :rules="{'required': fieldRequired}"
           :label="label"
           v-slot="{ field, meta }">
      <textarea class="form-control"
                :class="{ 'is-invalid': !meta.valid && meta.touched }"
                v-bind="field"
                :id="fieldId"
                :placeholder="fieldTitle"
                @input="$emit('update:modelValue', $event.target.value)"
                :readonly="!fieldEditable"
                style="height: 100px"
      ></textarea>
    </Field>
    <ErrorMessage :name="fieldId" class="invalid-feedback" />
  </div>

  <div class="mb-3" v-else-if="fieldType === 'file'">
    <p class="d-block mb-2 fw-medium" style="font-size: 18px">{{ fieldTitle }}</p>

    <div class="d-flex">
      <!-- static list -->
      <label class="btn btn-primary btn-soft btn-sm cursor-pointer position-relative">
        <Field :name="fieldId"
               :label="label"
               :rules="{'required': fieldRequired}"
               v-slot="{ handleChange, handleBlur, meta }">
          <input type="file"
                 :id="fieldId"
                 :name="fieldId"
                 @change="handleChange"
                 @input="handleChangeFile"
                 :data-file-ext="fieldAllowedExtensions"
                 data-file-max-size-kb-per-file="30000"
                 data-file-ext-err-msg="Дозволені формати:"
                 data-file-exist-err-msg="Файл вже вибрано:"
                 data-file-size-err-item-msg="Файл занадто великий!"
                 data-file-size-err-total-msg="Total allowed size exceeded!"
                 data-file-toast-position="bottom-center"
                 :data-file-preview-container="'#' + fieldId + '_preview'"
                 data-file-preview-img-height="60"
                 :data-file-btn-clear="'#' + fieldId + '_remove'"
                 data-file-preview-show-info="true"
                 data-file-preview-list-type="list"
                 :data-valid="meta.valid"
                 class="custom-file-input absolute-full"
                 :class="{ 'is-invalid': !meta.valid && meta.touched }">
        </Field>
        <span class="group-icon">
          <i class="fi fi-arrow-upload"></i>
          <i class="fi fi-circle-spin fi-spin"></i>
        </span>
        <span>Обрати файл</span>
      </label>

      <!-- remove button -->
      <a href="#"
         title="Очистити"
         data-bs-toggle="tooltip"
         :id="fieldId + '_remove'"
         class="js-file-input-btn-multiple-list-static-remove hide btn btn-secondary btn-sm ms-2">
        <i class="fi fi-close"></i>
        Очистити
      </a>
    </div>

    <div class="form-text">
      {{ fieldHelpText }}
    </div>

    <ErrorMessage :name="fieldId" class="invalid-feedback d-block"/>

    <div class="js-file-input-container-multiple-list-static position-relative hide-empty mt-2"
         :id="fieldId + '_preview'"><!-- container --></div>
  </div>

  <div class="mb-3" v-else-if="fieldType === 'file_multi'">
    <p class="d-block mb-2 fw-medium" style="font-size: 18px">{{ fieldTitle }}</p>

    <div class="d-flex">
      <!-- static list -->
      <label class="btn btn-primary btn-soft btn-sm cursor-pointer position-relative">
        <Field :name="fieldId"
               :label="label"
               :rules="{'required': fieldRequired}"
               v-slot="{ handleChange, handleBlur, meta }">
          <input multiple type="file"
                 :id="fieldId"
                 :name="fieldId"
                 @change="handleChange"
                 @input="handleChangeFile"
                 :data-file-ext="fieldAllowedExtensions"
                 data-file-max-size-kb-per-file="30000"
                 data-file-ext-err-msg="Дозволені формати:"
                 data-file-exist-err-msg="Файл вже вибрано:"
                 data-file-size-err-item-msg="Файл занадто великий!"
                 data-file-size-err-total-msg="Total allowed size exceeded!"
                 data-file-toast-position="bottom-center"
                 :data-file-preview-container="'#' + fieldId + '_preview'"
                 data-file-preview-img-height="60"
                 :data-file-btn-clear="'#' + fieldId + '_remove'"
                 data-file-preview-show-info="true"
                 data-file-preview-list-type="list"
                 class="custom-file-input absolute-full"
                 :class="{ 'is-invalid': !meta.valid && meta.touched }">
        </Field>
        <span class="group-icon">
          <i class="fi fi-arrow-upload"></i>
          <i class="fi fi-circle-spin fi-spin"></i>
        </span>
        <span>Обрати файл</span>
      </label>

      <!-- remove button -->
      <a href="#"
         title="Очистити"
         data-bs-toggle="tooltip"
         :id="fieldId + '_remove'"
         class="js-file-input-btn-multiple-list-static-remove hide btn btn-secondary btn-sm ms-2">
        <i class="fi fi-close"></i>
        Очистити
      </a>
    </div>

    <div class="form-text">
      {{ fieldHelpText }}
    </div>

    <ErrorMessage :name="fieldId" class="invalid-feedback d-block"/>

    <div class="js-file-input-container-multiple-list-static position-relative hide-empty mt-2"
         :id="fieldId + '_preview'"><!-- container --></div>
  </div>

</template>

<script>
import { Field, ErrorMessage } from 'vee-validate'

export default {
  name: "ClaimField",
  props: {
    modelValue: String,
    fieldType: String,
    fieldId: String,
    fieldTitle: String,
    fieldEditable: Boolean,
    fieldRequired: Boolean,
    fieldHelpText: String,
    fieldAllowedExtensions: String,
  },
  components: {
    Field,
    ErrorMessage
  },
  emits: ['update:modelValue'],
  mounted() {
    if (this.fieldType === 'file' || this.fieldType === 'file_multiple') {
      $.SOW.core.file_upload.init('input[type="file"].custom-file-input, input[type="file"].form-control');
    }
  },
  computed: {
    label() {
      return '"' + this.fieldTitle + '"'
    },
  },
  methods: {
    handleChangeFile(event) {
      this.$emit('update:modelValue', event.target.files)
    }
  }
}
</script>

<style scoped>

</style>
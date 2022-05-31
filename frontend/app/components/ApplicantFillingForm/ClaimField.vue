<template>
  <div class="form-floating mb-3" v-if="fieldType === 'text'">
    <input type="text"
           class="form-control"
           :id="fieldId"
           :placeholder="fieldTitle"
           v-model="modelValue"
           @input="$emit('update:modelValue', $event.target.value)"
           :disabled="!fieldEditable"
    >
    <label for="floatingInput">{{ fieldTitle }}</label>
  </div>
  <div class="form-floating mb-3" v-else-if="fieldType === 'email'">
    <input type="email"
           class="form-control"
           :id="fieldId"
           :placeholder="fieldTitle"
           v-model="modelValue"
           @input="$emit('update:modelValue', $event.target.value)"
           :disabled="!fieldEditable"
    >
    <label for="floatingInput">{{ fieldTitle }}</label>
  </div>
  <div class="form-floating mb-3" v-else-if="fieldType === 'date'">
    <input type="date"
           class="form-control"
           :id="fieldId"
           :placeholder="fieldTitle"
           v-model="modelValue"
           @input="$emit('update:modelValue', $event.target.value)"
           :disabled="!fieldEditable"
    >
    <label for="floatingInput">{{ fieldTitle }}</label>
  </div>
  <div class="form-floating mb-3" v-else-if="fieldType === 'textarea'">
    <textarea class="form-control"
              placeholder="Leave a comment here"
              :id="fieldId"
              :placeholder="fieldTitle"
              v-model="modelValue"
              @input="$emit('update:modelValue', $event.target.value)"
              :disabled="!fieldEditable"
              style="height: 100px"
    ></textarea>
    <label for="floatingInput">{{ fieldTitle }}</label>
  </div>
  <div class="mb-3" v-else-if="fieldType === 'file'">
    <p class="d-block mb-2 fw-medium" style="font-size: 18px">{{ fieldTitle }}</p>

    <div class="d-flex">
      <!-- static list -->
      <label class="btn btn-primary btn-sm cursor-pointer position-relative">
        <input type="file" :name="fieldId"
               data-file-ext="doc, docx"
               data-file-max-size-kb-per-file="30000"
               data-file-ext-err-msg="Allowed:"
               data-file-exist-err-msg="File already exists:"
               data-file-size-err-item-msg="File too large!"
               data-file-size-err-total-msg="Total allowed size exceeded!"
               data-file-toast-position="bottom-center"
               :data-file-preview-container="'#' + fieldId + '_preview'"
               data-file-preview-img-height="60"
               :data-file-btn-clear="'#' + fieldId + '_remove'"
               data-file-preview-show-info="true"
               data-file-preview-list-type="list"
               class="custom-file-input absolute-full">

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

    <div class="js-file-input-container-multiple-list-static position-relative hide-empty mt-2"
         :id="fieldId + '_preview'"><!-- container --></div>
  </div>
  <div class="mb-3" v-else-if="fieldType === 'file_multi'">
    <p class="d-block mb-2 fw-medium" style="font-size: 18px">{{ fieldTitle }}</p>

    <div class="d-flex">
      <!-- static list -->
      <label class="btn btn-primary btn-sm cursor-pointer position-relative">
        <input multiple type="file" :name="fieldId"
               data-file-ext="doc, docx"
               data-file-max-size-kb-per-file="30000"
               data-file-max-size-kb-total="0"
               data-file-max-total-files="100"
               data-file-ext-err-msg="Allowed:"
               data-file-exist-err-msg="File already exists:"
               data-file-size-err-item-msg="File too large!"
               data-file-size-err-total-msg="Total allowed size exceeded!"
               data-file-size-err-max-msg="Maximum allowed files:"
               data-file-toast-position="bottom-center"
               :data-file-preview-container="'#' + fieldId + '_preview'"
               data-file-preview-img-height="60"
               :data-file-btn-clear="'#' + fieldId + '_remove'"
               data-file-preview-show-info="true"
               data-file-preview-list-type="list"
               class="custom-file-input absolute-full">

        <span class="group-icon">
          <i class="fi fi-arrow-upload"></i>
          <i class="fi fi-circle-spin fi-spin"></i>
        </span>
        <span>Обрати файли</span>
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

    <div class="js-file-input-container-multiple-list-static position-relative hide-empty mt-2"
         :id="fieldId + '_preview'"><!-- container --></div>
  </div>
</template>

<script>
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
  },
  emits: ['update:modelValue'],
  mounted() {
    if (this.fieldType === 'file' || this.fieldType === 'file_multiple') {
      $.SOW.core.file_upload.init('input[type="file"].custom-file-input, input[type="file"].form-control');
    }
  }
}
</script>

<style scoped>

</style>
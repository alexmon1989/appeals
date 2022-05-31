<template>
  <div class="form-check mt-2 mb-4">
    <input class="form-check-input form-check-input-default"
           type="checkbox"
           :disabled="disabled"
           id="thirdPerson"
           v-model="modelValue"
           @input="$emit('update:modelValue', $event.target.checked)">
    <label class="form-check-label" for="thirdPerson">
      Апелянт - третя особа
    </label>
  </div>
</template>

<script>
export default {
  name: "ThirdPersonCheckbox",
  props: ['modelValue', 'disabled'],
  emits: ['update:modelValue'],
}
</script>

<style scoped>

</style>
<template>
  <div class="mb-3">
    <label class="form-label fw-medium" for="claim_kind">Вид звернення</label>
    <Field name="claim_kind"
           v-model="modelValue"
           rules="required"
           label="Об’єкт права інтелектуальної власності"
           v-slot="{ field, meta }">
      <select class="form-select"
              :disabled="claimKindsFiltered.length === 0"
              :class="{ 'is-invalid': !meta.valid && meta.touched }"
              @input="$emit('update:modelValue', parseInt($event.target.value))"
              id="claim_kind"
              v-bind="field"
      >
        <option value="" disabled selected="">Оберіть вид</option>
        <option v-for="claimKind in claimKindsFiltered" :value="claimKind.pk">
          {{ claimKind.title }}
        </option>
      </select>
    </Field>
    <ErrorMessage name="claim_kind" class="invalid-feedback"/>
  </div>
</template>

<script>
import { Field, ErrorMessage } from 'vee-validate'

export default {
  name: "ClaimKindSelect",
  props: {
    modelValue: Number,
    claimKinds: Array,
    objKindId: Number,
  },
  components: {
    Field,
    ErrorMessage,
  },
  emits: ['update:modelValue'],
  computed: {
    claimKindsFiltered() {
      return this.claimKinds.filter(x => x.obj_kind_id === this.objKindId);
    }
  }
}
</script>

<style scoped>

</style>
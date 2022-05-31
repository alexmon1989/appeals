<template>
  <div class="form-floating mb-3">
    <select class="form-select form-select-sm"
            id="claim_kind"
            :disabled="claimKindsFiltered.length === 0"
            v-model="modelValue"
            @input="$emit('update:modelValue', parseInt($event.target.value))">
      <option value="" disabled>Оберіть вид</option>
      <option v-for="claimKind in claimKindsFiltered" :value="claimKind.pk">
        {{ claimKind.title }}
      </option>
    </select>
    <label for="claim_kind">Вид звернення</label>
  </div>
</template>

<script>
export default {
  name: "ClaimKindSelect",
  props: {
    modelValue: Number,
    claimKinds: Array,
    objKindId: Number,
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
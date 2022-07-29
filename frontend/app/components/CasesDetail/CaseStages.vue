<template>
  <div class="d-flex justify-content-between align-items-center mb-4">
    <h4>Стадія розгляду</h4>
  </div>

  <!-- Simple Process Steps : Default -->
  <ol class="process-steps process-steps-primary text-muted mb-2">
    <li class="process-step-item"
        v-for="stage in stages"
        :class="{'complete': stage.status === 'done', 'active': stage.status === 'current'}"
    >{{ stage.number }}. {{ stage.title }}</li>
  </ol>
</template>

<script>
export default {
  name: "CaseStages",
  props: ['stages']
}
</script>

<style scoped>

</style>
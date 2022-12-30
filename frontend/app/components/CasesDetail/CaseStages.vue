<template>
  <div class="d-flex justify-content-between align-items-center mb-4">
    <h4>Стадія розгляду</h4>
  </div>

  <!-- Simple Process Steps : Default -->
  <ol class="process-steps process-steps-primary text-muted mb-2">
    <li class="process-step-item"
        v-for="stage in stages"
        :class="{
          'complete': stage.status === 'done' || (stopped && stage.number === 7 && stage.status !== 'not-active'),
          'active': stage.status === 'current',
          'paused': stage.status === 'paused',
          'stopped': stage.status === 'stopped' && stage.number !== 7,
        }"
    >{{ stage.number }}. {{ stage.title }}</li>
  </ol>

  <p><strong>Крок стадії:</strong> {{ stageStepTitle }} (код: <strong>{{ stageStepCode }}</strong>)</p>
  <div>
    <strong>Статус справи:</strong>&nbsp;
    <span v-if="stopped">Розгляд справи припинений</span>
    <span v-else-if="paused">Розгляд справи зупинений</span>
    <span v-else>Розгляд справи активний</span>
  </div>
</template>

<script>
export default {
  name: "CaseStages",
  props: ['stages', 'stageStepTitle', 'stageStepCode', 'paused', 'stopped']
}
</script>

<style scoped>
  .process-steps-primary > .stopped::before {
      background: #d3382e;
      border-color: #d3382e;
  }
  .process-steps-primary > .stopped {
    border-color: #d3382e;
  }

  .process-steps-primary > .paused::before {
      background: #57707c;
      border-color: #57707c;
  }
  .process-steps-primary > .paused {
    border-color: #57707c;
  }

</style>
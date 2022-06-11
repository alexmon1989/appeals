<template>
  <div>
    <b-alert v-for="alert in alerts" :key="alert.id" :variant="alert.variant" show>
      <!-- eslint-disable vue/no-v-html -->
      <div v-html="alert.html" />
      <!--eslint-enable-->
    </b-alert>
  </div>
</template>

<script>
  export default {
    name: 'Alerts',
    props: {
      alerts: {
        type: Array,
        default: () => ([])
      }
    }
  }
</script>

<style scoped>

</style>

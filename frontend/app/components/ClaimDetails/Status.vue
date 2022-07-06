<template>
  <div class="col-auto">
    <div class="text-muted text-uppercase fw-bold" id="claim-status">Статус:
      <span class="text-danger ms-1" v-if="claimData.status === 1">{{ claimData.status_verbal }}</span>
      <span class="text-primary ms-1" v-if="claimData.status === 2">{{ claimData.status_verbal }}</span>
      <span class="text-success ms-1" v-if="claimData.status === 3">{{ claimData.status_verbal }} №{{ claimData.case_number }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: "Status",
  props: ["claimData"],
}
</script>

<style scoped>

</style>
<template>
  <div class="overlay" id="overlay">
    <div class="overlay-content">
      <img :src="'/static/images/preloaders/loading.svg'" alt="Loading..."/>
      <div class="fw-bold fs-5 mt-n3" v-if="text">{{ text }}</div>
    </div>
  </div>
</template>

<script>
export default {
  props: ["text"],
  name: "Spinner"
}
</script>

<style scoped>

</style>
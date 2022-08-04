<template>
  <div class="row my-4">
    <div class="d-flex">
      <div class="text-muted text-uppercase me-3">Дата подання звернення:</div>
      <div class="fw-medium">{{ claimData.submission_date }}</div>
    </div>
  </div>

  <div class="row mb-3">
    <div class="col">
      <h2 class="h5 mb-3 text-indigo-800">Дані об'єкта</h2>

      <div class="text-muted text-uppercase">Об'єкт права інтелектуальної власності</div>
      <div class="fw-medium mb-3">{{ claimData.obj_kind }}</div>


      <div v-for="item in stages[3].items">
        <div class="text-muted text-uppercase">{{ item.title }}</div>
        <div class="fw-medium mb-3" v-html="processValue(item)"></div>
      </div>

      <div v-for="item in stages[4].items">
        <div class="text-muted text-uppercase">{{ item.title }}</div>
        <div class="fw-medium mb-3" v-html="processValue(item)"></div>
      </div>
    </div>

    <div class="col">
      <h2 class="h5 mb-3 text-indigo-800">{{ stages[5].title }}</h2>

      <div v-for="item in stages[5].items">
        <div class="text-muted text-uppercase">{{ item.title }}</div>
        <div class="fw-medium mb-3" v-html="processValue(item)"></div>
      </div>
    </div>

    <div class="col" v-if="stages[6].items && stages[6].items.length > 0">
      <h2 class="h5 mb-3 text-indigo-800">{{ stages[6].title }}</h2>

      <div v-for="item in stages[6].items">
        <div class="text-muted text-uppercase">{{ item.title }}</div>
        <div class="fw-medium mb-3" v-html="processValue(item)"></div>
      </div>
    </div>
  </div>

  <div class="row mb-3" v-if="stages[7].items.length > 0 || stages[8].items.length > 0">
      <div class="col" v-if="stages[7].items.length > 0">
          <h2 class="h5 mb-3 text-indigo-800">{{ stages[7].title }}</h2>

          <div v-for="item in stages[7].items">
            <div class="text-muted text-uppercase">{{ item.title }}</div>
            <div class="fw-medium mb-3" v-html="processValue(item)"></div>
          </div>
      </div>

      <div class="col" v-if="stages[8].items.length > 0">
          <h2 class="h5 mb-3 text-indigo-800">{{ stages[8].title }}</h2>

          <div v-for="item in stages[8].items">
            <div class="text-muted text-uppercase">{{ item.title }}</div>
            <div class="fw-medium mb-3" v-html="processValue(item)"></div>
          </div>
      </div>
  </div>
</template>

<script>
export default {
  name: "ClaimData",
  props: ["claimData", "stages",],
  methods: {
    processValue(item) {
      let res = item.value.replace(new RegExp('\r?\n','g'), '<br />')

      if (item.type === 'date' || item.id.includes('date')) {
        const segments = item.value.split('-')
        res = [segments[2], segments[1],segments[0]].join('.')
      }

      return res
    }
  }
}
</script>

<style scoped>

</style>
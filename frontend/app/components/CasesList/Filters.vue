<template>
  <div class="mb-4 border p-3">
      <div class="mb-3">
          <span class="me-3 fw-bold">Приналежність:</span>
          <div class="form-check form-check-inline">
              <input class="form-check-input form-check-input-primary"
                     type="radio"
                     name="users"
                     checked="checked"
                     id="inlineRadio1"
                     value="all"
                     v-model="users">
              <label class="form-check-label" for="inlineRadio1">Cправи усіх осіб</label>
          </div>
          <div class="form-check form-check-inline">
              <input class="form-check-input form-check-input-primary"
                     type="radio"
                     name="users"
                     id="inlineRadio2"
                     value="me"
                     v-model="users">
              <label class="form-check-label" for="inlineRadio2">Тільки мої справи</label>
          </div>
      </div>

      <div class="mb-3 ">
          <span class="me-3 fw-bold">Стадія:</span>
          <div class="form-check form-check-inline">
              <input class="form-check-input form-check-input-primary"
                     type="radio"
                     name="stage"
                     checked="checked"
                     id="inlineRadio3"
                     value="all"
                     v-model="stage">
              <label class="form-check-label" for="inlineRadio3">Усі стадії</label>
          </div>
          <div class="form-check form-check-inline">
              <input class="form-check-input form-check-input-primary"
                     type="radio"
                     name="stage"
                     id="inlineRadio4"
                     value="new"
                     v-model="stage">
              <label class="form-check-label" for="inlineRadio4">Нові справи</label>
          </div>
          <div class="form-check form-check-inline">
              <input class="form-check-input form-check-input-primary"
                     type="radio"
                     name="stage"
                     id="inlineRadio5"
                     value="processing"
                     v-model="stage">
              <label class="form-check-label" for="inlineRadio5">Справи в роботі</label>
          </div>
          <div class="form-check form-check-inline">
              <input class="form-check-input form-check-input-primary"
                     type="radio"
                     name="stage"
                     id="inlineRadio6"
                     value="finished"
                     v-model="stage">
              <label class="form-check-label" for="inlineRadio6">Закінчені справи</label>
          </div>
      </div>

      <div class="d-flex align-items-center">
          <span class="me-3 fw-bold">Вид ОПІВ:</span>
          <select class="form-select form-select-sm w-25" v-model="objKind">
              <option value="all">Усі види ОПІВ</option>
              <option :value="objKind.pk" v-for="objKind in objKinds">{{ objKind.title }}</option>
          </select>
      </div>
  </div>
</template>

<script>
export default {
  name: "Filters",
  props: ['objKinds'],
  data() {
    return {
      users: 'all',
      stage: 'all',
      objKind: 'all',
    }
  },
  methods: {
    emitFiltersChanged() {
      this.$emit(
          'filtersChanged',
          {
            users: this.users,
            stage: this.stage,
            objKind: this.objKind,
          }
      )
    }
  },
  watch: {
    users() {
      this.emitFiltersChanged()
    },
    stage() {
      this.emitFiltersChanged()
    },
    objKind() {
      this.emitFiltersChanged()
    },
  }
}
</script>

<style scoped>

</style>
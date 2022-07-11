<template>
  <div>
    <spinner v-if="loading"></spinner>
    <div class="min-vh-25" v-if="loading"></div>

    <div v-if="claims.length > 0">
      <!--
        data-autofill="false|hover|click"
        data-enable-paging="true"			 false = show all, no pagination
        data-items-per-page="10|15|30|50|100"
      -->
      <table class="table-datatable table table-bordered table-hover table-striped small"
             id="table-claims"
             data-lng-empty="No data available in table"
             data-lng-page-info="Записи від _START_ до _END_ з _TOTAL_ всього"
             data-lng-filtered="(filtered from _MAX_ total entries)"
             data-lng-loading="Loading..."
             data-lng-processing="Processing..."
             data-lng-search="Пошук..."
             data-lng-norecords="Результати відсутні"
             data-lng-sort-ascending=": activate to sort column ascending"
             data-lng-sort-descending=": activate to sort column descending"

             data-main-search="true"
             data-column-search="false"
             data-row-reorder="false"
             data-col-reorder="true"
             data-responsive="true"
             data-header-fixed="true"
             data-select-onclick="false"
             data-enable-paging="true"
             data-enable-col-sorting="true"
             data-autofill="false"
             data-group="false"
             data-items-per-page="15"

             data-enable-column-visibility="true"
             data-lng-column-visibility="Видимість стовбчиків"

             data-enable-export="false"
             data-custom-config='{
                  "stateSave": true,
                  "order": [[4, "desc"]]
                 }'>
        <thead>
        <tr>
          <th class="text-nowrap">№ заявки або ох. документа</th>
          <th class="text-nowrap">Тип об'єкта</th>
          <th class="text-nowrap">Вид звернення</th>
          <th>Статус</th>
          <th>Створено</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="claim in claims">
          <td><a :href="claim.absolute_url" class="fw-bold">{{ claim.obj_number }}</a></td>
          <td class="text-nowrap">{{ claim.obj_kind }}</td>
          <td>{{ claim.claim_kind }}</td>
          <td class="fw-bold">
            <span class="text-danger" v-if="claim.status === 1">{{ claim.status_display }}</span>
            <span class="text-primary" v-if="claim.status === 2">{{ claim.status_display }}</span>
            <span class="text-success" v-if="claim.status === 3">{{ claim.status_display }} №{{ claim.case_number }}</span>
          </td>
          <td class="text-nowrap" :data-sort="claim.created_at_timestamp ">{{ claim.created_at }}</td>
        </tr>
        </tbody>
        <tfoot>
        <tr>
          <th>№ заявки або ох. документа</th>
          <th>Тип об'єкта</th>
          <th>Вид звернення</th>
          <th>Статус</th>
          <th>Створено</th>
        </tr>
        </tfoot>
      </table>
    </div>

    <div v-else-if="!loading">
      <p class="mt-2">Звернення відсутні. Ви можете <a href="/filling/create-claim/">створити</a> ваше перше звернення.</p>
    </div>
  </div>

</template>

<script>
import { getTaskResult } from '@/app/src/until'
import Spinner from "../Spinner.vue"

export default {
  name: "ClaimsDataTable",

  components: {
    Spinner,
  },

  props: ['taskId'],
  data() {
    return {
      claims: [],
      loading: true,
      errors: [],
    }
  },
  async mounted() {
    try {
      this.claims = await getTaskResult(this.taskId)
      this.$nextTick(() => { $.SOW.vendor.datatables.init('.table-datatable') })

    } catch (e) {
      this.errors.push('Помилка 500. ПОмилка сервера.')
    } finally {
      this.loading = false
    }
  }
}
</script>

<style scoped>
</style>
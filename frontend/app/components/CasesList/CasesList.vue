<template>
  <filters :obj-kinds="objKinds" @filtersChanged="onFiltersChanged"></filters>

  <table class="table-datatable table table-bordered table-hover table-striped g-font-size-15"
         id="table-cases"
         ref="tableCases"
         data-lng-empty="Справи відсутні"
         data-lng-page-info="Записи від _START_ до _END_ з _TOTAL_ всього"
         data-lng-filtered="(filtered from _MAX_ total entries)"
         data-lng-loading="Завантаження..."
         data-lng-processing="Обробка..."
         data-lng-search="Пошук по назві, номеру справи, номеру заявки/ох.документа"
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
          "stateSave": false,
          "server-side": true,
          "processing": true,
          "serverSide": true,
          "ajax": "/api/cases/?format=datatables",
          "order": [],
          "columnDefs": [
              {
                  "targets": [2, 4],
                  "searchable": false
              }
          ]
       }'>
    <thead>
    <tr>
      <th data-data="case_number_link" data-name="case_number" class="text-nowrap">№ справи</th>
      <th data-data="claim.obj_number" class="text-nowrap">№ заявки або ох. документа</th>
      <th data-data="claim.obj_kind.title" class="text-nowrap">Вид ОПІВ</th>
      <th data-data="claim.obj_title" class="text-nowrap">Назва ОПІВ</th>
      <th data-data="claim.submission_date" class="text-nowrap">Дата подання звернення</th>
      <th data-data="stage_verbal" data-name="stage">Стадія</th>
    </tr>
    </thead>

    <tfoot>
    <tr>
      <th>№ справи</th>
      <th>№ заявки або ох. документа</th>
      <th>Вид ОПІВ</th>
      <th>Назва ОПІВ</th>
      <th>Дата подання звернення</th>
      <th>Стадія</th>
    </tr>
    </tfoot>
  </table>
</template>

<script>
import Filters from './Filters.vue'

export default {
  name: "CasesList",
  props: ['objKinds'],
  data() {
    return {
      baseAjaxUri: '/api/cases/?format=datatables',
    }
  },
  components: {
    Filters
  },
  methods: {
    onFiltersChanged(val) {
      const uriParams = new URLSearchParams(val).toString();
      const table = $(this.$refs.tableCases).DataTable()
      table.ajax.url( `${this.baseAjaxUri}&${uriParams}` ).load()
    }
  }
}
</script>

<style scoped>

</style>
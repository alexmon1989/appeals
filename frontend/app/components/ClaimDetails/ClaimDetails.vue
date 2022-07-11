<template>
  <div>
    <spinner v-if="loading"></spinner>

    <div class="alert alert-danger" role="alert" v-if="errors.length > 0">
      <ul class="list-unstyled mb-0">
        <li v-for="error in errors" v-html="error"></li>
      </ul>
    </div>

    <claim-details-header :objNumber="claimData.obj_number" v-if="claimData"></claim-details-header>

    <div class="section rounded mb-3" v-if="claimData">
      <div class="row mb-4">
        <div class="col">
          <h4>Детальна інформація звернення</h4>
        </div>

        <status :claim-data="claimData"></status>
      </div>

      <claim-stages :claim-data="claimData" :stages="stages"></claim-stages>

      <div class="row mb-3">
        <div class="col">
          <h2 class="h5 mb-3 text-indigo-800">Додатки</h2>
          <claim-attachments :documents-init="documents" :claim-data="claimData"></claim-attachments>
        </div>
      </div>

      <buttons :claim-id="claimData.id" :status="claimData.status"></buttons>
    </div>
  </div>

</template>

<script>
import {getTaskResult} from '@/app/src/until'
import ClaimAttachments from "../Attachments/ClaimAttachments.vue"
import ClaimDetailsHeader from "./Header.vue"
import Status from "./Status.vue"
import ClaimStages from "./ClaimStages.vue"
import Buttons from "./Buttons.vue"
import Spinner from "../Spinner.vue"

export default {
  props: ['taskId'],

  components: {
    ClaimAttachments,
    ClaimDetailsHeader,
    Status,
    ClaimStages,
    Buttons,
    Spinner,
  },

  data() {
    return {
      stages: false,
      documents: false,
      claimData: false,
      errors: [],
      loading: true,
    }
  },

  async mounted() {
    try {
      // Получение данных обращения
      const taskResult = await getTaskResult(this.taskId)
      if (Object.keys(taskResult).length === 0) {
        this.errors.push('<b>Помилка 404.</b> Звернення не існує.')
      } else {
        this.stages = taskResult.stages
        this.documents = taskResult.documents
        this.claimData = taskResult.claim_data

        document.title = this.claimData.obj_number + ' | Мої звернення'
      }
    } catch (e) {
      this.errors.push('<b>Помилка 500.</b> Помилка сервера.')
    } finally {
      this.loading = false
    }
  }
}
</script>

<style scoped>

</style>
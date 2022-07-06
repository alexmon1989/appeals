<template>
  <div class="d-flex justify-content-between mt-5 mb-3" v-if="status < 3">
    <div>
      <a data-href="{% url 'claim_delete' pk=claim.pk %}"
         class="js-ajax-confirm btn btn-danger"

         data-ajax-confirm-type="danger"

         data-ajax-confirm-size="modal-md"
         data-ajax-confirm-centered="false"

         data-ajax-confirm-title="Необхідне підтвердження"
         data-ajax-confirm-body="Ви впевнені, що хочете видалити це звернення?"

         data-ajax-confirm-btn-yes-class="btn-danger btn-sm"
         data-ajax-confirm-btn-yes-text="Підтвердити"
         data-ajax-confirm-btn-yes-icon="fi fi-check"

         data-ajax-confirm-btn-no-class="btn-secondary btn-sm"
         data-ajax-confirm-btn-no-text="Закрити"
         data-ajax-confirm-btn-no-icon="fi fi-close">
        <svg width="18px" height="18px" xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-x-lg"
             viewBox="0 0 16 16">
          <path fill-rule="evenodd"
                d="M13.854 2.146a.5.5 0 0 1 0 .708l-11 11a.5.5 0 0 1-.708-.708l11-11a.5.5 0 0 1 .708 0Z"></path>
          <path fill-rule="evenodd"
                d="M2.146 2.146a.5.5 0 0 0 0 .708l11 11a.5.5 0 0 0 .708-.708l-11-11a.5.5 0 0 0-.708 0Z"></path>
        </svg>
        Видалити</a>

      <a :href="'/filling/claim-update/' + claimId + '/'" class="btn btn-warning">
        <svg width="18px" height="18px" xmlns="http://www.w3.org/2000/svg" fill="currentColor"
             class="bi bi-pencil-square" viewBox="0 0 16 16">
          <path
              d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"></path>
          <path fill-rule="evenodd"
                d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5v11z"></path>
        </svg>
        Редагувати</a>
    </div>

    <a href="#" :data-href="'/filling/case-create/' + claimId + '/'"
       class="js-ajax-confirm btn btn-primary"

       data-ajax-confirm-mode="ajax"
       data-ajax-confirm-type="secondary"

       data-ajax-confirm-title="Необхідне підтвердження"
       data-ajax-confirm-body="Ви впевнені що хочете передати звернення на розгляд?"

       data-ajax-confirm-btn-yes-class="btn-sm btn-primary"
       data-ajax-confirm-btn-yes-text="Так"
       data-ajax-confirm-btn-yes-icon="fi fi-check"

       data-ajax-confirm-btn-no-class="btn-sm btn-light"
       data-ajax-confirm-btn-no-text="Ні"
       data-ajax-confirm-btn-no-icon="fi fi-close"
       data-ajax-confirm-callback-function="_myCustomFunc"
    >
      <svg width="18px" height="18px" xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-check-lg"
           viewBox="0 0 16 16">
        <path
            d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022Z"></path>
      </svg>
      Подати на розгляд</a>
  </div>
</template>

<script>
export default {
  name: "Buttons",
  props: ["status", "claimId"],
  mounted() {
     $.SOW.core.ajax_confirm.init('.js-ajax-confirm')
  }
}
</script>

<style scoped>

</style>
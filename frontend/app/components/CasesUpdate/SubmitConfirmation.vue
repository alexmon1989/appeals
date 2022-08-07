<template>
  <!-- Small -->
  <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#exampleModalSm">
    <svg width="18px" height="18px" xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-save" viewBox="0 0 16 16">
      <path d="M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H9.5a1 1 0 0 0-1 1v7.293l2.646-2.647a.5.5 0 0 1 .708.708l-3.5 3.5a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L7.5 9.293V2a2 2 0 0 1 2-2H14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h2.5a.5.5 0 0 1 0 1H2z"></path>
    </svg>
    Зберегти
  </button>

  <!-- Modal -->
  <div class="modal fade" id="exampleModalSm" tabindex="-1" role="dialog" aria-labelledby="exampleModalLabelSm"
       aria-hidden="true">
    <div class="modal-dialog" role="document">
      <div class="modal-content">

        <div class="modal-header border-0 bg-primary-soft">
          <h5 class="modal-title" id="exampleModalLabelSm">Необхідне підтвердження</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>

        <div class="modal-body">
          Ви впевнені, що бажаєте зберегти дані?
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-sm btn-primary" @click="save">
            <i class="fi fi-check"></i>
            Так, зберегти
          </button>
          <button type="button" class="btn btn-sm btn-secondary" data-bs-dismiss="modal">
            <i class="fi fi-close"></i>
            Закрити
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SubmitConfiramation",
  methods: {
    save() {
      document.getElementById('case-update-form').submit()
    }
  }
}
</script>

<style scoped>

</style>
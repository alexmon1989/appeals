<template>
  <header>
      <div class="row g-1 align-items-center">
          <div class="col">
              <h1 class="h4">{{ objNumber }}</h1>
              <nav aria-label="breadcrumb">
                  <ol class="breadcrumb small">
                      <li class="breadcrumb-item"><a href="/filling/">АС "Апеляційні справи"</a></li>
                      <li class="breadcrumb-item"><a href="/filling/">Список моїх звернень</a></li>
                      <li class="breadcrumb-item text-muted active" aria-current="page">{{ objNumber }}</li>
                  </ol>
              </nav>
          </div>
      </div>
  </header>
</template>

<script>
export default {
  name: "Header",
  props: ['objNumber']
}
</script>

<style scoped>

</style>
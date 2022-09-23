<template>
  <a href="#"
     @click="onClickBtn"
     id="dropdownNotificationOptions"
     class="btn btn-sm btn-light rounded-circle text-primary-hover dropdown-toggle" data-bs-toggle="dropdown"
     data-bs-auto-close="outside" aria-expanded="false" aria-haspopup="true" aria-label="Notifications">

    <!-- svg icon -->
    <span style="margin-top: -3px;">
      <svg width="24px" height="24px" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <g stroke="none" stroke-width="1" fill="none" fill-rule="evenodd">
          <path fill="currentColor"
                d="M17,12 L18.5,12 C19.3284271,12 20,12.6715729 20,13.5 C20,14.3284271 19.3284271,15 18.5,15 L5.5,15 C4.67157288,15 4,14.3284271 4,13.5 C4,12.6715729 4.67157288,12 5.5,12 L7,12 L7.5582739,6.97553494 C7.80974924,4.71225688 9.72279394,3 12,3 C14.2772061,3 16.1902508,4.71225688 16.4417261,6.97553494 L17,12 Z"></path>

          <!-- animate-blink -->
          <rect v-if="showNewNotificationsAnimation" class="animate-blink"
                fill="red" opacity="0.8"
                x="10"
                y="16"
                width="4"
                height="4"
                rx="2"></rect>
          <!-- no animate -->
          <rect v-else fill="#000000" opacity="0.3" x="10" y="16" width="4" height="4" rx="2"></rect>
        </g>
      </svg>
    </span>
  </a>

  <div aria-labelledby="dropdownNotificationOptions"
       id="notifications-dropdown"
       class="dropdown-menu dropdown-menu-clean dropdown-menu-navbar-autopos dropdown-fadeindown end-0 p-0 mt-2 w-300">

    <div v-if="loading">
      <div class="py-5 text-gray-600 text-center">Завантаження сповіщень...</div>
    </div>
    <div v-else>
      <div v-if="newNotificationsCount > 0">
        <div class="dropdown-header p-3">Нових сповіщень: {{ newNotificationsCount }}</div>
        <div class="dropdown-divider"></div>
      </div>

      <div class="max-vh-50 scrollable-vertical">
        <div class="py-5 text-gray-400 text-center" v-if="notifications.length === 0">Сповіщення відсутні</div>

        <!-- item -->
        <div class="clearfix dropdown-item fw-medium p-3 border-bottom border-light overflow-hidden"
             v-for="item in notifications">
          <!-- badge -->
          <span class="badge bg-success float-end fw-normal mt-1" v-if="!item.read">нове</span>

          <p class="small fw-bold m-0 text-wrap" v-html="item.message"></p>
          <small class="d-block smaller fw-normal text-muted">{{ item.created_at }}</small>
        </div>
        <!-- /item -->
      </div>
    </div>
    <div class="dropdown-divider mb-0"></div>
    <a href="/notifications/"
       class="prefix-icon-ignore dropdown-footer dropdown-custom-ignore fw-medium py-3 text-primary">
      Дивитися усі
    </a>
  </div>
</template>

<script>
import {getCookie} from "../../src/until";

export default {
  name: "Widget",
  data() {
    return {
      newNotificationsCount: 0,
      notifications: [],
      notificationListUrl: '/notifications/api/list/?limit=20',
      newNotificationCountUrl: '/notifications/api/new-count/',
      notificationsMarkAsRead: '/notifications/api/mark-as-read/',
      showNewNotificationsAnimation: false,
      loading: false,
    }
  },
  async mounted() {
    this.newNotificationsCount = await this.getNewNotificationsCount()
    this.showNewNotificationsAnimation = this.newNotificationsCount > 0

    // Проверка на наличие новых оповещений каждые 15 сек
    window.setInterval(async () => {
      // Если виджет раскрыт, то не нужно получать количество новых оповещений
      if (!this.opened() && !this.showNewNotificationsAnimation) {
        // Получение оповещений
        this.newNotificationsCount = await this.getNewNotificationsCount()
        this.showNewNotificationsAnimation = this.newNotificationsCount > 0
      }
    }, 15000); // interval set to one sec.
  },
  methods: {
    // Получение списка последних оповещений
    async getNotifications() {
      let response = await fetch(this.notificationListUrl)
      if (response.ok) { // если HTTP-статус в диапазоне 200-299
        return await response.json()
      } else {
        console.log("Error getting notifications: " + response.status);
      }
    },

    // Получение количества новых оповещений
    async getNewNotificationsCount() {
      let response = await fetch(this.newNotificationCountUrl)
      if (response.ok) { // если HTTP-статус в диапазоне 200-299
        const res = await response.json()
        return res.count
      } else {
        console.log("Error getting new notifications count: " + response.status);
      }
    },

    // Пометка оповещений как прочитанных
    async markNotificationsAsRead() {
      const response = await fetch(this.notificationsMarkAsRead, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken')
          }
        })
        if (!response.ok) { // если HTTP-статус не в диапазоне 200-299
          console.log("Error marking notifications as read: " + response.status);
        }
    },

    // Открыт ли список оповещений
    opened() {
      const style = window.getComputedStyle(document.getElementById('notifications-dropdown'));
      return (style.display !== 'none')
    },

    // Обработчик события нажатия на иконку оповещений
    async onClickBtn() {
      this.notifications = []
      this.newNotificationsCount = 0
      // Проверка видимый ли выпадающий список с оповещениями, чтобы не делать лишний запрос на сервер
      if (this.opened()) {
        this.showNewNotificationsAnimation = false
        this.loading = true

        // Получение оповещений и количества новых оповещений
        this.newNotificationsCount = await this.getNewNotificationsCount()
        this.notifications = await this.getNotifications()

        this.loading = false

        // Пометка оповещений как прочитанных
        await this.markNotificationsAsRead()
      }
    }
  },
}
</script>

<style scoped>

</style>
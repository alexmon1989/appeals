from django.urls import path

from . import views


urlpatterns = [
    path('', views.list_index, name='notifications-list'),
    path('api/list/', views.NotificationList.as_view(), name='notifications-list-api'),
    path('api/new-count/', views.NewNotificationsCountView.as_view(), name='notifications-new-count'),
    path('api/mark-as-read/', views.MarkNotificationsAsRead.as_view(), name='notifications-mark-as-read')
]

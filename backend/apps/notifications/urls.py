from django.urls import path

from . import views


urlpatterns = [
    path('', views.list_index, name='notifications-list'),
]

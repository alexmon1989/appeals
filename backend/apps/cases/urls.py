from django.urls import path

from . import views

urlpatterns = [
    path('', views.cases_list, name='cases-list'),
]

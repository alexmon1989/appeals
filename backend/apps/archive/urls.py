from django.urls import path

from . import views


urlpatterns = [
    path('', views.CaseListView.as_view(), name='archive-cases-list'),
]

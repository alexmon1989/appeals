from django.urls import path

from . import views

urlpatterns = [
    path('', views.cases_list, name='cases-list'),
    path('<int:pk>/', views.CaseDetailView.as_view(), name='cases-detail'),
]

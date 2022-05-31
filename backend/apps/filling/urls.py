from django.urls import path

from . import views


urlpatterns = [
    path('', views.my_applications_list, name='my-applications-list'),
    path('create-application', views.create_application, name='create_application')
]

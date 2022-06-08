from django.urls import path

from . import views


urlpatterns = [
    path('', views.my_applications_list, name='my-applications-list'),
    path('create-claim', views.create_claim, name='create_claim')
]

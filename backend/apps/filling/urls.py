from django.urls import path

from . import views


urlpatterns = [
    path('', views.MyClaimsListView.as_view(), name='my-claims-list'),
    path('create-claim', views.CreateClaimView.as_view(), name='create_claim')
]

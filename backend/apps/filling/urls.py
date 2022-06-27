from django.urls import path

from . import views


urlpatterns = [
    path('', views.MyClaimsListView.as_view(), name='my-claims-list'),
    path('create-claim', views.CreateClaimView.as_view(), name='create_claim'),
    path('claim-detail/<int:pk>/', views.ClaimDetailView.as_view(), name='claim_detail'),
    path('claim-status/<int:pk>/', views.claim_status, name='claim_status'),
    path('claim-delete/<int:pk>/', views.claim_delete, name='claim_delete'),
    path('claim-update/<int:pk>/', views.ClaimUpdateView.as_view(), name='claim_update'),
    path('case_create/<int:claim_id>/', views.case_create, name='case_create_from_claim')
]

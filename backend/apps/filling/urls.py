from django.urls import path

from . import views


urlpatterns = [
    path('', views.MyClaimsListView.as_view(), name='my-claims-list'),
    path('create-claim/', views.CreateClaimView.as_view(), name='create_claim'),
    path('claim-detail/<int:pk>/', views.ClaimDetailView.as_view(), name='claim_detail'),
    path('claim-status/<int:pk>/', views.claim_status, name='claim_status'),
    path('claim-delete/<int:pk>/', views.claim_delete, name='claim_delete'),
    path('claim-update/<int:pk>/', views.ClaimUpdateView.as_view(), name='claim_update'),
    path('case-create/<int:claim_id>/', views.case_create, name='case_create_from_claim'),
    path('get-data-from-sis/', views.get_data_from_sis, name='get_data_from_sis'),
    path('get-task-result/<str:task_id>/', views.get_task_result, name='get_task_result'),
    path('get-filling-form-data/', views.get_filling_form_data, name='get_filling_form_data'),
    path('set-message/<str:level>/<str:message>/', views.set_message, name='set_message'),
    path(
        'create-files-with-signs-info/<int:claim_id>/',
        views.create_files_with_signs_info,
        name='create_files_with_signs_info'
    ),
]

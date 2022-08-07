from django.urls import path

from . import views


urlpatterns = [
    path('', views.cases_list, name='cases-list'),
    path('detail/<int:pk>/', views.CaseDetailView.as_view(), name='cases-detail'),
    path('update/<int:pk>/', views.CaseUpdateView.as_view(), name='cases_update'),
    path('upload-sign/<int:document_id>/', views.upload_sign, name='upload-sign'),
    path('document-signs-info/<int:document_id>/', views.document_signs_info, name='document-signs-info'),
    path('take_to_work/<int:pk>/', views.take_to_work, name='cases_take_to_work'),

    path('ds-file/', views.ds_file, name='cases_ds_file'),
    path('ds-token/', views.ds_token, name='cases_ds_token'),
    path('ds-iframe/', views.ds_iframe, name='cases_ds_iframe'),
    path('decisions/<str:date>', views.decisions, name='cases_decisions'),
]

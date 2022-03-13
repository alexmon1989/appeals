from django.urls import path

from . import views

urlpatterns = [
    path('', views.cases_list, name='cases-list'),
    path('detail/<int:pk>/', views.CaseDetailView.as_view(), name='cases-detail'),
    path('create/', views.CaseCreateView.as_view(), name='cases-create'),
    path('upload-sign/<int:document_id>/', views.upload_sign, name='upload-sign'),
    path('ds-file/', views.ds_file, name='cases_ds_file'),
    path('ds-token/', views.ds_token, name='cases_ds_token'),
    path('ds-iframe/', views.ds_iframe, name='cases_ds_iframe'),
]

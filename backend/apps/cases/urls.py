from django.urls import path

from . import views


urlpatterns = [
    path('', views.cases_list, name='cases-list'),
    path('detail/<int:pk>/', views.CaseDetailView.as_view(), name='cases-detail'),
    path('update/<int:pk>/', views.CaseUpdateView.as_view(), name='cases_update'),
    path('upload-sign-external/<int:document_id>/', views.upload_sign_external, name='upload-sign-external'),
    path('upload-sign-internal/<int:document_id>/', views.upload_sign_internal, name='upload-sign-internal'),
    path('document-signs-info/<int:document_id>/', views.document_signs_info, name='document-signs-info'),
    path('document-history/<int:document_id>/', views.document_history, name='document-history'),
    path('take_to_work/<int:pk>/', views.take_to_work, name='cases_take_to_work'),
    path('create-collegium/<int:pk>/', views.CaseCreateCollegium.as_view(), name='case_create_collegium'),
    path('pause/<int:pk>/', views.CasePausingView.as_view(), name='case_pausing'),
    path('stop/<int:pk>/', views.CaseStoppingView.as_view(), name='case_stopping'),
    path('renew-consideration/<int:pk>/', views.case_renew_consideration, name='case_renew_consideration'),
    path(
        'create-pre-meeting-protocol/<int:pk>/',
        views.case_create_pre_meeting_protocol,
        name='case_create_pre_meeting_protocol'
    ),
    path(
        'create-files-with-signs-info/<int:case_id>/',
        views.create_files_with_signs_info,
        name='cases_create_files_with_signs_info'
    ),
    path(
        'consider-for-acceptance/<int:pk>/',
        views.CaseConsiderForAcceptance.as_view(),
        name='case_consider_for_acceptance'
    ),
    path('meeting/<int:pk>/', views.CaseMeetingView.as_view(), name='case_meeting'),
    path(
        'case-info/<int:pk>/',
        views.CaseInfoPDFView.as_view(),
        name='case_info',
    ),
    path(
        'add-document/<int:pk>/',
        views.DocumentAddView.as_view(),
        name='case_add_document'
    ),
    path(
        'delete-document/<int:pk>/',
        views.document_delete,
        name='case_delete_document'
    ),
    path(
        'document-send-to-sign/<int:pk>/',
        views.document_send_to_sign,
        name='document_send_to_sign'
    ),
    path(
        'document-send-to-chancellary/<int:pk>/',
        views.document_send_to_chancellary,
        name='document_send_to_chancellary'
    ),
    path(
        'update-document/<int:pk>/',
        views.DocumentUpdateView.as_view(),
        name='case_update_document'
    ),
    path('user-finished-cases/<int:user_id>/', views.cases_get_finished_cases, name='cases_get_finished_cases'),
    path('user-current-cases/<int:user_id>/', views.cases_get_current_cases, name='cases_get_current_cases'),

    path('ds-file/', views.ds_file, name='cases_ds_file'),
    path('ds-token/', views.ds_token, name='cases_ds_token'),
    path('ds-iframe/', views.ds_iframe, name='cases_ds_iframe'),
    path('decisions/<str:date>', views.decisions, name='cases_decisions'),
]

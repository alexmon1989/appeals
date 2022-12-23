from django.urls import path

from . import views


urlpatterns = [
    path('', views.TicketListView.as_view(), name='support-index'),
    path('create/', views.TicketCreateView.as_view(), name='support-create-ticket'),
    path('detail/<int:pk>/', views.TicketDetailView.as_view(), name='support-detail-ticket'),
    path('delete/<int:pk>/', views.delete_ticket, name='support-delete-ticket'),
    path('take-to-work/<int:pk>/', views.take_to_work, name='support-take-to-work'),
    path('close/<int:pk>/', views.TicketCloseView.as_view(), name='support-ticket-close'),
]

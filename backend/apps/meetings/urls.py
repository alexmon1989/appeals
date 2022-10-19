from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='meetings-index'),
    path('calendar-events/', views.ListEventsAPIView.as_view(), name='meetings-calendar-events'),
    path('event-detail/', views.EventDetailAPIView.as_view(), name='meetings-event-detail'),
    path('absence-create/', views.AbsenceCreateView.as_view(), name='meetings-absence-create'),
    path('absence-delete/<int:pk>/', views.delete_absence, name='meetings-delete-absence'),
    path('invitation-accept/<int:pk>/', views.invitation_accept, name='meetings-invitation-accept'),
    path('invitation-reject/<int:pk>/', views.invitation_reject, name='meetings-invitation-reject'),
]

from django.urls import path
from django.conf import settings
from . import views


if settings.AUTH_METHOD == 'ds':
    urlpatterns = [
        path('login-ds/', views.login_view_ds_file, name='login'),
    ]
else:
    urlpatterns = [
        path('login-common/', views.CustomLoginView.as_view(), name='login'),
        # path('logout/', views.CustomLogoutView.as_view(), name='logout'),
        path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
        path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    ]

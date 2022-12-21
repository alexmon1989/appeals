"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView

from rest_framework import routers

from apps.cases import views as cases_views


router = routers.DefaultRouter()
router.register(r'cases', cases_views.CasesViewSet, basename='Case')
router.register(r'cases/(?P<id>\d+)/documents', cases_views.DocumentsViewSet, basename='Document')
router.register(r'cases/(?P<id>\d+)/history', cases_views.CaseHistoryViewSet, basename='CaseHistory')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='filling/' if settings.AUTH_METHOD == 'ds' else 'cases/', permanent=True)),
    path('api/cases/published/', cases_views.CasePublishedListAPIView.as_view()),
    path('api/', include(router.urls)),
    path('cases/', include('apps.cases.urls')),
    path('filling/', include('apps.filling.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('search/', include('apps.search.urls')),
    path('statistics/', include('apps.stats.urls')),
    path('meetings/', include('apps.meetings.urls')),
    path('payments/', include('apps.payments.urls')),

    path('users/', include('apps.users.urls')),
    path('users/', include('django.contrib.auth.urls')),

    path('select2/', include('django_select2.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
] # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

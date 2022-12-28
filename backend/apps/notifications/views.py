from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import NotificationSerializer
from .services import (notification_get_user_notifications_qs,
                       notification_get_user_new_notifications_count,
                       notification_mark_notifications_as_read)


@login_required
def list_index(request):
    return render(request, template_name='notifications/list/index.html')


class NotificationList(generics.ListAPIView):
    """Возвращает JSON со всеми оповещениями пользователя."""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return notification_get_user_notifications_qs(self.request.user.pk)

    def list(self, request, *args, **kwargs):
        # Если нужно ограничить количество результатов
        if self.request.GET.get('limit'):
            try:
                limit = int(self.request.GET['limit'])
            except ValueError:
                pass
            else:
                queryset = self.get_queryset()[:limit]
                serializer = NotificationSerializer(queryset, many=True)
                return Response(serializer.data)
        return super().list(request, *args, **kwargs)


class NewNotificationsCountView(APIView):
    """Возвращает количество новых оповещений пользователя."""
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get(self, request, format=None):
        count = notification_get_user_new_notifications_count(self.request.user.pk)
        return Response({'count': count})


class MarkNotificationsAsRead(APIView):
    """Помечает оповещения пользователя как прочитанные."""
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def post(self, request, format=None):
        notification_mark_notifications_as_read(self.request.user.pk)
        return Response({'success': 1})

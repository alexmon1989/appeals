from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import NotificationSerializer
from .services import notification_get_user_notifications_qs


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

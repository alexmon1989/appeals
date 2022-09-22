from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')

    class Meta:
        model = Notification
        fields = '__all__'

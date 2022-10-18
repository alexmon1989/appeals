from abc import ABC, abstractmethod
from typing import Iterable

from django.db.models import QuerySet

from .models import Notification as Notification


def notification_get_user_notifications_qs(user_id: int) -> QuerySet[Notification]:
    """Возвращает queryset со всеми оповещениями пользователя."""
    return Notification.objects.filter(addressee_id=user_id).order_by('-created_at')


def notification_get_user_new_notifications_count(user_id: int) -> int:
    """Возвращает количество новых оповещений пользователя."""
    return notification_get_user_notifications_qs(user_id).exclude(read=True).count()


def notification_mark_notifications_as_read(user_id: int) -> None:
    """Возвращает количество новых оповещений пользователя."""
    notification_get_user_notifications_qs(user_id).update(read=True)


class Channel(ABC):
    """Абстрактный класс для оповещений."""
    @abstractmethod
    def notify(self, message: str, user_id: int):
        """Оповещение пользователя о событии."""
        pass


class DbChannel(Channel):
    """Канал оповещений с помощью базы данных (модель Notification)."""
    def notify(self, message: str, user_id: int):
        Notification.objects.create(
            addressee_id=user_id,
            message=message,
            level=Notification.Level.SUCCESS
        )


class Service:
    """Сервис оповещения пользователей."""
    def __init__(self, channels: Iterable[Channel] = None):
        if not channels:
            channels = []
        self.channels = channels

    def execute(self, message: str, users_ids: Iterable[int], channels: Iterable[Channel] = None):
        if not channels:
            channels = []
        channels = channels or self.channels  # Приоритет каналам оповещений, указанным как аргумент
        for channel in channels:
            for user_id in users_ids:
                channel.notify(message, user_id)

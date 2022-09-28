from abc import ABC, abstractmethod
from typing import Iterable

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from .models import Notification as Notification


UserModel = get_user_model()


class Notifier(ABC):
    """Абстрактный класс для оповещений пользователей."""
    _allowed_levels = ['debug', 'info', 'success', 'warning','error']

    @abstractmethod
    def notify(self, message: str, level: str):
        """Оповещение пользователя о событии."""
        pass


class AlertNotifier(Notifier):
    """Класс, задачей которого является оповещение пользователя о событии посредством django.messages."""
    _msg_types = {
        'debug': messages.debug,
        'info': messages.info,
        'success': messages.success,
        'warning': messages.warning,
        'error': messages.error,
    }

    def __init__(self, request):
        self.request = request

    def notify(self, message: str, level: str):
        if level in self._allowed_levels:
            self._msg_types[level](self.request, message)


class MultipleUsersNotifier(Notifier, ABC):

    @abstractmethod
    def set_addressees(self, addressees=None):
        pass


class UsersDbNotifier(MultipleUsersNotifier):
    """Класс, задачей которого является оповещение пользователей о событии посредством БД."""
    addressees: Iterable[UserModel]

    def __init__(self, addressees=None):
        self.set_addressees(addressees)

    def set_addressees(self, addressees: Iterable[UserModel] = None):
        self.addressees = addressees or []

    def notify(self, message: str, level: str):
        if level in self._allowed_levels:
            for addressee in self.addressees:
                Notification.objects.create(
                    addressee=addressee,
                    message=message,
                    level=level
                )


def notification_get_user_notifications_qs(user_id: int) -> QuerySet[Notification]:
    """Возвращает queryset со всеми оповещениями пользователя."""
    return Notification.objects.filter(addressee_id=user_id).order_by('-created_at')


def notification_get_user_new_notifications_count(user_id: int) -> int:
    """Возвращает количество новых оповещений пользователя."""
    return notification_get_user_notifications_qs(user_id).exclude(read=True).count()


def notification_mark_notifications_as_read(user_id: int) -> None:
    """Возвращает количество новых оповещений пользователя."""
    notification_get_user_notifications_qs(user_id).update(read=True)

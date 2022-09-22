from abc import ABC, abstractmethod
from typing import Iterable

from django.contrib import messages
from django.contrib.auth import get_user_model

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
    """Класс, задачей которого является оповещение пользователей о событии посредством django.messages."""
    addressees: Iterable[UserModel]

    def __init__(self, addressees=None):
        self.set_addressees(addressees)

    def set_addressees(self, addressees=None):
        self.addressees = addressees or []

    def notify(self, message: str, level):
        if level in self._allowed_levels:
            for addressee in self.addressees:
                Notification.objects.create(
                    addressee=addressee,
                    message=message,
                    level=level
                )

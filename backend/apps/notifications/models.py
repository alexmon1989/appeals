from django.db import models
from django.contrib.auth import get_user_model

from apps.common.models import TimeStampModel


UserModel = get_user_model()


class Notification(TimeStampModel):
    """Модель оповещения."""
    class Level(models.TextChoices):
        DEBUG = 'debug'
        INFO = 'info'
        SUCCESS = 'success'
        WARNING = 'warning'
        ERROR = 'error'

    addressee = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        verbose_name="Особа, якій адресовано повідомлення",
    )
    message = models.CharField('Текст повідомлення', max_length=255)
    level = models.CharField('Рівень повідомлення', max_length=10, choices=Level.choices, default=Level.INFO)
    read = models.BooleanField('Прочитано адресатом', default=False)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = 'Сповіщення'
        verbose_name_plural = 'Сповіщення'
        db_table = 'notifications_notifications_list'

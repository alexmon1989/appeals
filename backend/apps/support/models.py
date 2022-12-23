from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model

from apps.common.models import TimeStampModel


UserModel = get_user_model()
ALLOWED_EXTENSIONS = ['jpg', 'gif', 'png']


class Ticket(TimeStampModel):
    """Модель обращения в тех. поддержку"""
    class StatusChoices(models.IntegerChoices):
        NEW = 1, 'Нове'
        PENDING = 2, 'У роботі'
        DONE = 3, 'Виконано'

    status = models.IntegerField('Статус', choices=StatusChoices.choices, default=StatusChoices.NEW)
    send_by = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        verbose_name="Автор заявки",
        null=True,
        blank=True,
        related_name='send_by',
    )
    text = models.TextField(
        'Текст заявки',
        max_length=2048,
        help_text='Будь ласка, детально опишіть проблему'
    )

    file_1 = models.FileField(
        'Файл 1',
        upload_to='tickets/%Y/%m/%d/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        help_text='Файл з зображенням (формати: jpg, gif, png)'
    )
    file_2 = models.FileField(
        'Файл 2',
        upload_to='tickets/%Y/%m/%d/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        help_text='Файл з зображенням (формати: jpg, gif, png)'
    )
    file_3 = models.FileField(
        'Файл 3',
        upload_to='tickets/%Y/%m/%d/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)],
        help_text='Файл з зображенням (формати: jpg, gif, png)'
    )

    taken_to_work_by = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        verbose_name="Прийняв у роботу",
        null=True,
        blank=True,
        related_name='taken_to_work_by'
    )
    taken = models.DateTimeField('Дата та час прийняття у роботу', null=True, blank=True)

    closed_by = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        verbose_name="Закрив",
        null=True,
        blank=True,
        related_name='closed_by'
    )
    closed = models.DateTimeField('Дата та час закриття заявки', null=True, blank=True)

    comment = models.TextField('Коментар', null=True, blank=True)

    def __str__(self):
        return f"Заявка №{self.pk}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

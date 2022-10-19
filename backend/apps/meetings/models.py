from django.db import models
from django.contrib.auth import get_user_model

from apps.cases.models import Case
from apps.common.models import TimeStampModel


UserModel = get_user_model()


class Meeting(TimeStampModel):
    """Модель заседания."""
    datetime = models.DateTimeField('Дата та час засідання')
    case = models.ForeignKey(Case, verbose_name='Справа', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Засідання'
        verbose_name_plural = 'Засідання'

    def __str__(self):
        return f"{self.case.case_number} - {self.datetime}"


class Invitation(TimeStampModel):
    """Модель приглашения на заседание."""
    meeting = models.ForeignKey(Meeting, verbose_name='Засідання', on_delete=models.CASCADE)
    user = models.ForeignKey(UserModel, verbose_name='Член колегії', on_delete=models.CASCADE)
    accepted_at = models.DateTimeField('Дата та час прийняття запрошення', blank=True, null=True)
    rejected_at = models.DateTimeField('Дата та час відмовлення у запрошенні', blank=True, null=True)

    class Meta:
        verbose_name = 'Запрошення'
        verbose_name_plural = 'Запрошення'

    def __str__(self):
        return f"{str(self.meeting)} - {self.user.get_full_name_initials()}"


class Absence(TimeStampModel):
    """Модель отсутствия на работе сотрудника АП."""
    date_from = models.DateField('Дата з')
    date_to = models.DateField('Дата по')
    user = models.ForeignKey(UserModel, verbose_name='Член колегії', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Відсутність співробітника АП'
        verbose_name_plural = 'Відсутності співробітників АП'

    def __str__(self):
        return f"{self.user.get_full_name_initials()} - з {self.date_from} по {self.date_to}"

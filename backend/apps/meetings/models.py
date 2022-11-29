from django.db import models
from django.contrib.auth import get_user_model

from apps.cases.models import Case
from apps.common.models import TimeStampModel


UserModel = get_user_model()


class Meeting(TimeStampModel):
    """Модель заседания."""
    class MeetingTypeChoices(models.TextChoices):
        PRE = 'PRE', 'Підготовче засідання'
        COMMON = 'COMMON', 'Апеляційне засідання'

    class MeetingStatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Очікує'
        DONE = 'DONE', 'Проведено'

    datetime = models.DateTimeField('Дата та час засідання')
    case = models.ForeignKey(Case, verbose_name='Справа', on_delete=models.CASCADE)
    meeting_type = models.CharField(
        'Тип засідання',
        choices=MeetingTypeChoices.choices,
        default=MeetingTypeChoices.COMMON,
        max_length=6
    )
    status = models.CharField(
        'Статус засідання',
        choices=MeetingStatusChoices.choices,
        default=MeetingStatusChoices.PENDING,
        max_length=16
    )

    class Meta:
        verbose_name = 'Засідання'
        verbose_name_plural = 'Засідання'

    def __str__(self):
        return f"{self.case.case_number} - {self.datetime}"

    @property
    def accept_count(self):
        """Количество принявших приглашение."""
        return self.invitation_set.filter(accepted_at__isnull=False).count()


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
    reason = models.CharField('Причина', max_length=255, default='')
    user = models.ForeignKey(UserModel, verbose_name='Член колегії', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Відсутність співробітника АП'
        verbose_name_plural = 'Відсутності співробітників АП'

    def __str__(self):
        return f"{self.user.get_full_name_initials()} - з {self.date_from} по {self.date_to}"

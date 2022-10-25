from django.db import models
from django.contrib.auth import get_user_model

from apps.common.models import TimeStampModel
from apps.cases.models import Case


UserModel = get_user_model()


class Payment(TimeStampModel):
    """Модель платежу."""
    title = models.CharField('Назва плетежу', max_length=255)
    bop_id = models.PositiveIntegerField('ID у системі БОП', null=True, blank=True)
    case = models.ForeignKey(Case, verbose_name='Справа', null=True, blank=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(
        UserModel,
        verbose_name='Ким зараховано',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    approved_at = models.DateTimeField(verbose_name='Час зарахування', null=True, blank=True)

    class Meta:
        verbose_name = 'Платіж'
        verbose_name_plural = 'Платежі'
        db_table = 'payments_list'

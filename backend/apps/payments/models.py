from django.db import models
from django.contrib.auth import get_user_model

from apps.common.models import TimeStampModel
from apps.cases.models import Case


UserModel = get_user_model()


class Payment(TimeStampModel):
    """Модель платежу."""
    title = models.CharField('Назва плетежу', max_length=255)
    value = models.FloatField('Сума')
    payment_date = models.DateField('Дата оплати')
    bop_id = models.PositiveIntegerField('ID у системі БОП', null=True, blank=True)
    cases = models.ManyToManyField(Case, verbose_name='Справи', blank=True, through='PaymentCase')

    class Meta:
        verbose_name = 'Платіж'
        verbose_name_plural = 'Платежі'
        db_table = 'payments_payments_list'

    def __str__(self):
        return self.title


class PaymentCase(TimeStampModel):
    """Связующая таблица между платежами и ап. делами."""
    case = models.ForeignKey(Case, verbose_name='Справа', on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, verbose_name='Платіж', on_delete=models.CASCADE)
    approved_by = models.ForeignKey(
        UserModel,
        verbose_name='Ким зараховано',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    approved_at = models.DateTimeField(verbose_name='Час зарахування', null=True, blank=True)

    class Meta:
        db_table = 'payments_payments_cases'
        verbose_name = 'Справа'
        verbose_name_plural = 'Справи'

from django.db import models
from django.contrib.auth import get_user_model

from backend.core.models import TimeStampModel
from ..classifiers.models import ObjKind, ClaimKind, DocumentName, DocumentType


UserModel = get_user_model()


class Case(TimeStampModel):
    """Модель дела."""
    case_number = models.CharField('Номер справи', max_length=255, blank=True, null=True)
    app_number = models.CharField('Номер заявки (охоронного документа)', max_length=255)
    obj_kind = models.ForeignKey(
        ObjKind,
        on_delete=models.SET_NULL,
        verbose_name="Вид об'єкта промислової власності",
        null=True,
    )
    claim_kind = models.ForeignKey(
        ClaimKind,
        on_delete=models.SET_NULL,
        verbose_name="Вид заяви/заперечення",
        null=True,
    )
    obj_title = models.CharField("Назва об'єкта", max_length=255)
    applicant_name = models.CharField("Найменування апелянта (заявника)", max_length=255)
    applicant_represent = models.CharField("Найменування представника апелянта", max_length=255, blank=True)
    mailing_address = models.CharField("Адреса для листування", max_length=255, blank=True)
    collegium = models.ManyToManyField(
        UserModel,
        verbose_name='Члени колегії',
        related_name='collegium',
        through='CollegiumMembership'
    )
    secretary = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        verbose_name="Секретар",
        null=True,
        related_name='secretary',
    )
    expert = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        verbose_name="Експерт",
        null=True,
        blank=True,
        related_name='expert',
    )
    papers_owner = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        verbose_name="Особа, у якої знаходиться паперова справа",
        null=True,
        blank=True,
        related_name='papers_owner',
    )
    claim_date = models.DateField('Дата подання заперечення (заяви)', null=True, blank=True)
    deadline = models.DateField('Дата, до якої необхідно розглянути заперечення', null=True, blank=True)
    hearing = models.DateField('Дата призначенного засідання', null=True, blank=True)

    def __str__(self):
        return f"{self.obj_title} ({self.app_number})"

    class Meta:
        verbose_name = 'Справа'
        verbose_name_plural = 'Справи'
        db_table = 'cases_cases_list'


class Document(TimeStampModel):
    """Модель документа дела."""
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True, verbose_name='Справа')
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, verbose_name='Тип документа')
    document_name = models.ForeignKey(
        DocumentName, on_delete=models.SET_NULL, null=True, verbose_name='Назва документа'
    )
    registration_number = models.CharField('Реєстраційний номер', max_length=255, null=True, blank=True)
    registration_date = models.DateField('Дата реєстрації', null=True, blank=True)
    output_date = models.DateField('Дата відправлення', null=True, blank=True)
    input_date = models.DateField('Дата отримання', null=True, blank=True)

    def __str__(self):
        if self.case.case_number:
            return f"{self.document_name} (номер справи: {self.case.case_number})"
        return self.document_name

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документи'
        db_table = 'cases_documents_list'


class CollegiumMembership(models.Model):
    """Связующая таблица апелляционного дела и членов коллегии"""
    person = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    is_head = models.BooleanField(default=False)

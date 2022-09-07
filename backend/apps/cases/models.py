from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from ..common.models import TimeStampModel
from ..classifiers.models import ObjKind, ClaimKind, DocumentType, RefusalReason
from .utils import sign_get_file_path, document_get_original_file_path

from ..filling.models import Claim

from pathlib import Path
import urllib.parse
import os


UserModel = get_user_model()


class Case(TimeStampModel):
    """Модель дела."""
    claim = models.OneToOneField(Claim, on_delete=models.SET_NULL, verbose_name='Звернення', null=True, blank=True)
    case_number = models.CharField('Номер справи', max_length=255, blank=True, null=True)
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
    deadline = models.DateField('Дата, до якої необхідно розглянути звернення', null=True, blank=True)
    hearing = models.DateField('Дата призначенного засідання', null=True, blank=True)
    stage_step = models.ForeignKey('CaseStageStep', on_delete=models.SET_NULL, verbose_name='Етап стадії розгляду',
                                   null=True, blank=True)
    archived = models.BooleanField('Передано в архів', default=False)
    refusal_reasons = models.ManyToManyField(
        RefusalReason,
        verbose_name='Підстави для відмови у наданні правової охорони',
        blank=True,
    )

    def __str__(self):
        return self.case_number

    class Meta:
        verbose_name = 'Справа'
        verbose_name_plural = 'Справи'
        db_table = 'cases_cases_list'


class CaseStage(TimeStampModel):
    """Модель стадии дела."""
    title = models.CharField('Назва стадії', max_length=255)
    number = models.PositiveSmallIntegerField('Номер стадії', null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Стадія справи'
        verbose_name_plural = 'Стадії справи'
        db_table = 'cases_stage'


class CaseStageStep(TimeStampModel):
    """Модель этапа стадии дела."""
    title = models.CharField('Назва етапу', max_length=1024)
    stage = models.ForeignKey(CaseStage, on_delete=models.CASCADE, verbose_name='Стадія')
    code = models.PositiveIntegerField('Код етапу')
    case_stopped = models.BooleanField('Діловодство припинено', default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Етап стадії справи'
        verbose_name_plural = 'Етапи стадій справ'
        db_table = 'cases_stage_step'


class CaseHistory(TimeStampModel):
    """Модель истории дела."""
    action = models.CharField('Дія', max_length=1024)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, verbose_name='Справа')
    user = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Користувач",
    )

    def __str__(self):
        return self.action

    class Meta:
        verbose_name = 'Дія по справі'
        verbose_name_plural = 'Дії по справі'
        db_table = 'cases_history'


class Document(TimeStampModel):
    """Модель документа дела."""
    claim = models.ForeignKey(Claim, on_delete=models.SET_NULL, null=True, verbose_name='Звернення')
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True, verbose_name='Справа')
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, verbose_name='Тип документа')
    registration_number = models.CharField('Реєстраційний номер', max_length=255, null=True, blank=True)
    barcode = models.CharField('Штрихкод', max_length=255, null=True, blank=True)
    registration_date = models.DateTimeField('Дата реєстрації', null=True, blank=True)
    output_date = models.DateTimeField('Дата відправлення', null=True, blank=True)
    input_date = models.DateTimeField('Дата отримання', null=True, blank=True)
    file = models.FileField(
        verbose_name='Оригінальний файл документа',
        upload_to=document_get_original_file_path
    )
    auto_generated = models.BooleanField('Сгенеровано автоматично', default=False)
    claim_document = models.BooleanField(
        'Подано або сформовано під час подання звернненя',
        default=False
    )

    @property
    def signed_file_url(self):
        """Возвращает путь к файлу с информацией о цифровых подписях."""
        path = Path(self.file.name)
        stem = urllib.parse.quote_plus(path.stem)
        return self.file.url.replace(stem, f"{stem}_signs")

    @property
    def signed_file(self):
        """Возвращает путь к файлу с информацией о цифровых подписях."""
        path = Path(self.file.name)
        return str(path).replace(path.stem, f"{path.stem}_signs")

    @property
    def folder_path(self):
        """Возвращает путь к каталогу с файлами."""
        path = Path(self.file.path)
        return str(path.parent)

    def assign_file(self, file_path: Path, file_name: str = None):
        """Присваивает файл документу."""
        with open(file_path, "rb") as fh:
            with ContentFile(fh.read()) as file_content:
                self.file.save(file_name or file_path.name, file_content)
                self.save()
        os.remove(file_path)

    def __str__(self):
        return self.document_type.title

    def save(self, *args, **kwargs):
        """Переопределение метода сохранения для обеспечения структуры каталогов."""
        if self.id is None:
            saved_file = self.file
            self.file = None
            super().save(*args, **kwargs)
            self.file = saved_file
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документи'
        db_table = 'documents'


class CollegiumMembership(models.Model):
    """Связующая таблица апелляционного дела и членов коллегии"""
    person = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name='Особа')
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    is_head = models.BooleanField(default=False, verbose_name='Голова колегії')

    class Meta:
        verbose_name = 'Колегія'
        verbose_name_plural = 'Колегія'
        db_table = 'cases_collegium_membership'


class Sign(TimeStampModel):
    """Цифровая подпись документа."""
    document = models.ForeignKey(Document, verbose_name='Документ', on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=sign_get_file_path,
        verbose_name='Файл з цифровим підписом (.p7s)'
    )
    file_signed = models.FileField(
        verbose_name='Підписаний файл'
    )
    user = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        verbose_name="Користувач",
        null=True,
    )
    subject = models.CharField('Підписант', max_length=255)
    serial_number = models.CharField('Серійний номер', max_length=255)
    issuer = models.CharField('Надавач послуг (АЦСК)', max_length=255)
    timestamp = models.CharField('Мітка часу', max_length=255)

    def __str__(self):
        return f"{self.document.case.case_number} - {self.document.document_type} - {self.subject}"

    def save(self, *args, **kwargs):
        """Переопределение метода сохранения для обеспечения структуры каталогов."""
        if self.id is None:
            saved_file = self.file
            self.file = None
            super().save(*args, **kwargs)
            self.file = saved_file
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Цифровий підпис'
        verbose_name_plural = 'Цифрові підписи'
        db_table = 'documents_signs'

from django.db import models
from django.contrib.auth import get_user_model

from ..common.models import TimeStampModel
from ..classifiers.models import ObjKind, ClaimKind, DocumentType
from .utils import sign_get_file_path, document_get_original_file_path

from ..filling.models import Claim

from pathlib import Path


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

    def __str__(self):
        return self.case_number

    class Meta:
        verbose_name = 'Справа'
        verbose_name_plural = 'Справи'
        db_table = 'cases_cases_list'


class Document(TimeStampModel):
    """Модель документа дела."""
    claim = models.ForeignKey(Claim, on_delete=models.SET_NULL, null=True, verbose_name='Звернення')
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True, verbose_name='Справа')
    document_type = models.ForeignKey(DocumentType, on_delete=models.SET_NULL, null=True, verbose_name='Тип документа')
    registration_number = models.CharField('Реєстраційний номер', max_length=255, null=True, blank=True)
    registration_date = models.DateField('Дата реєстрації', null=True, blank=True)
    output_date = models.DateField('Дата відправлення', null=True, blank=True)
    input_date = models.DateField('Дата отримання', null=True, blank=True)
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
    def signed_file(self):
        """Возвращает путь к файлу с информацией о цифровых подписях."""
        path = Path(self.file.name)
        return str(path).replace(path.stem, f"{path.stem}_signs")

    @property
    def folder_path(self):
        """Возвращает путь к каталогу с файлами."""
        path = Path(self.file.path)
        return str(path.parent)

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
        return f"{self.document.case.case_number} - {self.document.document_name} - {self.subject}"

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


class DocumentTemplate(TimeStampModel):
    """Модель шаблона документа."""
    title = models.CharField('Назва шаблону', max_length=512)
    file = models.FileField('Файл', upload_to='doc-templates/')
    documents_types = models.ManyToManyField(DocumentType, verbose_name='Типи документів', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Шаблон документу'
        verbose_name_plural = 'Шаблони документів'
        db_table = 'documents_templates'

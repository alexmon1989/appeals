from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator

from apps.common.models import TimeStampModel
from apps.classifiers.models import ObjKind, ClaimKind, DocumentType, RefusalReason, DecisionType, CommandType
from .utils import sign_get_file_path, document_get_original_file_path

from apps.filling.models import Claim

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
    stopped = models.BooleanField('Розгляд справи припинений', default=False)
    paused = models.BooleanField('Діловодство по справі зупинене', default=False)
    archived = models.BooleanField('Передано в архів', default=False)
    refusal_reasons = models.ManyToManyField(
        RefusalReason,
        verbose_name='Підстави для відмови у наданні правової охорони',
        blank=True,
    )
    addressee = models.CharField('Адресат', max_length=255, null=True, blank=True)
    address = models.CharField('Адреса', max_length=255, null=True, blank=True)
    decision_type = models.ForeignKey(
        DecisionType,
        on_delete=models.SET_NULL,
        verbose_name='Рішення Апеляційної палати',
        null=True,
        blank=True
    )
    decision_date = models.DateField('Дата оголошення рішення АП', null=True, blank=True)

    def __str__(self):
        return self.case_number

    @property
    def collegium_head(self) -> UserModel:
        """Глава коллегии."""
        item = self.collegiummembership_set.filter(is_head=True).first()
        return item.person if item else None

    @property
    def has_unsigned_docs(self) -> bool:
        """Имеет ли дело неподписанные документы."""
        return self.document_set.filter(sign__timestamp='').exists()

    @property
    def has_pre_meeting_doc(self) -> bool:
        """Имеет ли дело документ протокола подгтовительного заседания."""
        for doc in self.document_set.all():
            if doc.document_type.code == '0027':
                return True
        return False

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
        upload_to=document_get_original_file_path,
        validators=[FileExtensionValidator(['pdf', 'docx', 'doc', 'xlsx', 'xls', 'jpg', 'jpeg', 'png', 'gif'])]
    )
    auto_generated = models.BooleanField('Сгенеровано автоматично', default=False)
    claim_document = models.BooleanField(
        'Подано або сформовано під час подання звернненя',
        default=False
    )
    can_be_edited = models.BooleanField(
        'Може бути відредагований до підписання',
        default=True
    )
    converted_to_pdf = models.BooleanField('Конвертовано у pdf', default=False)
    deleted = models.BooleanField('Видалено', default=False)

    @property
    def is_signed_by_head(self) -> bool:
        """Подписан ли документ главой АП или его заместителем."""
        for sign in self.sign_set.all():
            if sign.timestamp:  # Документ подписан, а не ждёт подписания
                for group in sign.user.groups.all():
                    if group.name in ('Голова Апеляційної палати', 'Заступник голови Апеляційної палати'):
                        return True
        return False

    @property
    def is_signed(self) -> bool:
        """Подписан ли документ всеми подписантами."""
        res = False
        for sign in self.sign_set.all():
            if not sign.timestamp:  # Документ подписан, а не ждёт подписания
                res = False
                break
            res = True
        return res

    @property
    def signed_file_url(self):
        """Возвращает путь к подписанному файлу."""
        path = Path(self.file.name)
        if self.converted_to_pdf:  # документ конвертирован в pdf
            name = urllib.parse.quote_plus(path.name)
            stem = urllib.parse.quote_plus(path.stem)
            return self.file.url.replace(name, f"{stem}_signs.pdf")

        stem = urllib.parse.quote_plus(path.stem)
        return self.file.url.replace(stem, f"{stem}_signs")

    @property
    def signed_file_name(self):
        """Возвращает название подписанного файла."""
        path = Path(self.file.name)
        if self.converted_to_pdf:  # документ конвертирован в pdf
            return f"{path.stem}_signs.pdf"
        return f"{path.stem}_signs{path.suffix}"

    @property
    def signed_file(self):
        """Возвращает путь к файлу, который был подписан."""
        path = Path(self.file.name)
        if self.converted_to_pdf:  # документ конвертирован в pdf
            return str(path).replace(path.name, f"{path.stem}_signs.pdf")
        return str(path).replace(path.stem, f"{path.stem}_signs")

    @property
    def can_be_sent_to_sign(self):
        """Может ли документ быть передан на подпись."""
        return self.auto_generated and self.case and self.sign_set.count() == 0

    @property
    def is_sent_to_sign(self) -> bool:
        """Передан на подпись."""
        return self.sign_set.count() > 0

    @property
    def have_to_be_signed(self) -> bool:
        """Должен ли быть подписан."""
        return (self.auto_generated and self.sign_set.count() == 0) or \
               (self.sign_set.count() > 0 and self.sign_set.filter(timestamp='').exists())

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

    def can_be_updated(self, user: UserModel):
        """Можно ли загрузить новый файл для документа."""
        # Проверка секретаря дела, сгенерирован ли документ автоматически и не подписан ли
        return self.case and self.case.secretary == user and self.auto_generated and self.can_be_edited \
               and not self.is_signed

    def can_be_deleted(self, user: UserModel):
        """Может ли пользователь удалить документ (удалять можно только вторичные документы)."""
        return self.case and self.case.secretary == user and not self.auto_generated and not self.barcode

    @property
    def sent_to_chancellary(self) -> bool:
        """Был ли документ отправлен в АС Вихідні документи"""
        return self.command_set.filter(command_type__command_name='send_to_chancellary').exists()

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


class DocumentHistory(TimeStampModel):
    """Модель истории документа."""
    action = models.CharField('Дія', max_length=1024)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, verbose_name='Документ')
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
        verbose_name = 'Дія по документу'
        verbose_name_plural = 'Дії по документу'
        db_table = 'documents_history'


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


class PostalProtocolExchange(models.Model):
    id_rec = models.AutoField(primary_key=True)
    id_cead = models.IntegerField(blank=True, null=True)
    saved_at = models.DateTimeField(blank=True, null=True)
    send_to_chancellary = models.DateTimeField(blank=True, null=True)
    send_to_recipient = models.DateTimeField(blank=True, null=True)
    date_of_receiving = models.DateTimeField(blank=True, null=True)
    date_of_postal_return = models.DateTimeField(blank=True, null=True)
    postal_return_reason = models.CharField(max_length=250, blank=True, null=True)
    cancel_sending_document_date = models.DateTimeField(blank=True, null=True)
    cancel_sending_document_reason = models.CharField(max_length=250, blank=True, null=True)
    doc = models.ForeignKey(Document, models.DO_NOTHING, blank=True, null=True)
    command = models.ForeignKey('Command', models.SET_NULL, db_column='id_command', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'postal_protocol_exchange'


class Command(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_command')
    command_type = models.ForeignKey(CommandType, on_delete=models.SET_NULL, blank=True, null=True,
                                     db_column='id_type_comm')
    create_date = models.DateTimeField(blank=True, null=True)
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, blank=True, null=True, db_column='id_document')
    execution_date = models.DateTimeField(blank=True, null=True)
    is_done = models.BooleanField(blank=True, null=True)
    is_error = models.BooleanField(blank=True, null=True)
    error_datetime = models.DateTimeField(blank=True, null=True)
    error_message = models.CharField(max_length=1024, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ls_list_commands'


class EsignProtocolExchange(models.Model):
    """Протокол підписання документу зовнішнім сервісом."""
    id_rec = models.AutoField(primary_key=True)
    doc = models.ForeignKey(Document, models.DO_NOTHING, blank=True, null=True)
    id_cead = models.IntegerField(blank=True, null=True)
    command = models.ForeignKey('Command', models.SET_NULL, db_column='id_command', blank=True, null=True)
    date_saved_at = models.DateTimeField(blank=True, null=True)
    date_export_to_esignserice = models.DateTimeField(blank=True, null=True)
    date_import_from_esignservice = models.DateTimeField(blank=True, null=True)
    date_signed = models.DateTimeField(blank=True, null=True)
    esign_body = models.BinaryField(blank=True, null=True)
    signer_name = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'esign_protocol_exchange'

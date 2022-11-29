from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.functional import cached_property

from apps.common.models import TimeStampModel
from apps.classifiers.models import ClaimKind, ObjKind

import json


UserModel = get_user_model()


class ClaimField(TimeStampModel):
    """Модель поля обращения, которое зависит от типа обращения."""

    class FieldType(models.TextChoices):
        TEXT = 'text', 'Текстове поле'
        EMAIL = 'email', 'E-Mail'
        TEXTAREA = 'textarea', 'Текстова область'
        DATE = 'date', 'Поле вибору дати'
        FILE = 'file', 'Поле вибору файла'
        FILE_MULTIPLE = 'file_multi', 'Поле вибору файла (мультивибір)'

    title = models.CharField('Назва', max_length=1024)
    help_text = models.TextField('Допоміжний текст', max_length=1024, blank=True, null=True)
    input_id = models.CharField('ID поля вводу', max_length=32)
    claim_kind = models.ForeignKey(
        ClaimKind,
        on_delete=models.SET_NULL,
        verbose_name='Тип звернення',
        null=True
    )
    field_type = models.CharField(
        'Тип поля',
        max_length=10,
        choices=FieldType.choices,
        default=FieldType.TEXT
    )
    allowed_extensions = models.CharField(
        'Дозволені формати файлу',
        max_length=255,
        blank=True,
        null=True,
        help_text='Перелічте дозволені формати через кому (напр, ".doc, .docx"). '
                  'Має ефект тільки якщо тип поля - "Поле вибору файла".'
    )
    stage = models.PositiveIntegerField(
        'Етап вводу на формі',
        choices=(
            (3, '3. Номер заявки/охоронного документа'),
            (4, '4. Дані об\'єкта права інтелектуальної власності'),
            (5, '5. Відомості про заявника (апелянта) та власника'),
            (6, '6. Відомостей про апелянта (лише у випадку заперечень 3-х осіб і апеляційних заяв)'),
            (7, '7. Додаткова інформація'),
            (8, '8. Відомості щодо рішення Укрпатенту'),
            (9, '9. Додатки (файли)'),
        )
    )
    editable = models.BooleanField('Можливо редагувати', default=True)
    required = models.BooleanField('Обов\'язкове до заповнення', default=True)
    enabled = models.BooleanField('Включено', default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Поле звернення"
        verbose_name_plural = "Поля звернень"


class Claim(TimeStampModel):
    """Модель обращения."""
    obj_kind = models.ForeignKey(ObjKind, on_delete=models.CASCADE, verbose_name='Тип об\'єкта')
    claim_kind = models.ForeignKey(ClaimKind, on_delete=models.CASCADE, verbose_name='Вид звернення')
    obj_number = models.CharField('Номер заявки або охоронного документа', max_length=255)
    obj_title = models.CharField('Назва ОПІВ', max_length=1024)
    third_person = models.BooleanField('Апелянт - третя особа', default=False)
    status = models.PositiveIntegerField(
        'Статус',
        choices=(
            (1, 'Потребує підписання документів'),
            (2, 'Готове до подання'),
            (3, 'Створено справу'),
        ),
        default=1
    )
    user = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        verbose_name="Користувач",
        null=True,
    )
    submission_date = models.DateTimeField(verbose_name='Дата та час подачі', null=True, blank=True)
    json_data = models.TextField('Дані звернення', blank=True, null=True)
    internal_claim = models.BooleanField('Заявка створена у внутрішньому модулі', default=False)

    def __str__(self):
        return self.obj_number

    @cached_property
    def data(self):
        """Возвращает распарсенный json с данными обращения."""
        return json.loads(self.json_data)

    def get_absolute_url(self):
        return reverse('claim_detail', kwargs={'pk': self.pk})

    def get_appellant_title(self):
        """Возвращает имя апеллянта """
        if self.third_person:
            appellant_name = self.data['third_person_applicant_title']
        else:
            appellant_name = self.data['applicant_title']
        return appellant_name.replace("\r\n", ", ")

    def get_appellant_address(self):
        """Возвращает адрес апеллянта """
        if self.third_person:
            appellant_address = self.data['third_person_applicant_address']
        else:
            appellant_address = self.data['applicant_address']
        return appellant_address.replace("\r\n", ", ")

    def get_applicant_title(self):
        """Возвращает имя заявителя заявки на объект пром. собств."""
        try:
            applicant_title = self.data['applicant_title']
            return applicant_title.replace("\r\n", ", ")
        except KeyError:
            return ''

    def get_applicant_address(self):
        """Возвращает адрес заявителя заявки на объект пром. собств."""
        try:
            applicant_address = self.data['applicant_address']
            return applicant_address.replace("\r\n", ", ")
        except KeyError:
            return ''

    def get_owner_title(self):
        """Возвращает данные владельца охранного документа """
        try:
            applicant_title = self.data['owner_title']
            return applicant_title.replace("\r\n", ", ")
        except KeyError:
            return ''

    def get_owner_address(self):
        """Возвращает адрес владельца охранного документа """
        try:
            owner_address = self.data['owner_address']
            return owner_address.replace("\r\n", ", ")
        except KeyError:
            return ''

    def get_represent_title(self, third_person: bool = False):
        """Возвращает имя представителя."""
        try:
            if third_person:
                # Апеллянт - 3-е лицо
                represent_title = self.data['third_person_represent_title']
            else:
                # Апеллянт - заявитель
                represent_title = self.data['represent_title']
            return represent_title.replace("\r\n", ", ")
        except KeyError:
            return ''

    def get_represent_address(self, third_person: bool = False):
        """Возвращает адрес представителя."""
        try:
            if third_person:
                # Апеллянт - 3-е лицо
                represent_address = self.data['third_person_represent_address']
            else:
                # Апеллянт - заявитель
                represent_address = self.data['represent_address']
            return represent_address.replace("\r\n", ", ")
        except KeyError:
            return ''

    class Meta:
        verbose_name = "Звернення"
        verbose_name_plural = "Звернення"

from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from backend.core.models import TimeStampModel
from ..classifiers.models import ClaimKind, ObjKind


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
    third_person = models.BooleanField('Апелянт - третя особа', default=False)
    status = models.PositiveIntegerField(
        'Статус',
        choices=(
            (1, 'Потребує підписання документів'),
            (2, 'Очікує передачі на розгляд'),
            (3, 'Передано на розгляд'),
            (4, 'Створено справу'),
        ),
        default=1
    )
    user = models.ForeignKey(
        UserModel,
        on_delete=models.SET_NULL,
        verbose_name="Користувач",
        null=True,
    )
    json_data = models.TextField('Дані звернення', blank=True, null=True)

    def __str__(self):
        return self.obj_number

    def get_absolute_url(self):
        return reverse('claim_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = "Звернення"
        verbose_name_plural = "Звернення"

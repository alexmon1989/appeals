from django.db import models
from ..common.models import TimeStampModel


class ObjKind(TimeStampModel):
    """Модель вида объекта ИС."""
    title = models.CharField("Назва", max_length=255)
    sis_id = models.PositiveSmallIntegerField("Id типу об'єкта у СІС", null=True, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вид об'єкта промислової власності"
        verbose_name_plural = "Види об'єктів промислової власності"
        db_table = 'cl_obj_kinds'


class ClaimKind(TimeStampModel):
    """Модель вида заявления/возражения."""
    class ObjStateChoices(models.IntegerChoices):
        APPLICATION = 1, 'Заявка' # заявка
        PROTECTIVE_DOC = 2, 'Охоронний документ'  # охранный документ

    class ClaimSenseChoices(models.TextChoices):
        DENIAL = 'DE', 'Заперечення'
        APPEAL = 'AP', 'Апеляційна заява'

    title = models.CharField("Назва", max_length=255)
    template_title = models.CharField("Назва для шаблону MS Word", max_length=255, null=True, blank=True)
    obj_kind = models.ForeignKey(
        ObjKind,
        on_delete=models.SET_NULL,
        verbose_name="Вид об'єкта промислової власності",
        null=True,
    )
    third_person = models.BooleanField("3-тя особа", default=False)
    obj_state = models.PositiveIntegerField(
        'Статус об\'єкта',
        choices=ObjStateChoices.choices,
        default=ObjStateChoices.APPLICATION
    )
    claim_sense = models.CharField(
        'Суть типу звернення',
        choices=ClaimSenseChoices.choices,
        null=True,
        blank=True,
        max_length=2
    )

    def __str__(self):
        return f"{self.obj_kind.title}: {self.title}"

    class Meta:
        verbose_name = "Вид заяви/заперечення"
        verbose_name_plural = "Види заяв/заперечень"
        db_table = 'cl_claim_kinds'


class DocumentType(TimeStampModel):
    """Модель типа документа."""

    class Origin(models.TextChoices):
        INTERNAL = 'internal', 'Внутрішній'
        EXTERNAL = 'external', 'Зовнішній'

    class Direction(models.TextChoices):
        INPUT = 'internal', 'Вхідний'
        OUTPUT = 'external', 'Вихідний'

    title = models.CharField("Назва", max_length=512)
    direction = models.CharField("Напрямок", max_length=16, choices=Direction.choices, null=True, blank=True)
    origin = models.CharField("Походження", max_length=16, choices=Origin.choices, null=True, blank=True)
    code = models.CharField("Код (ідентифікатор) документа", null=True, blank=True, max_length=255)
    muc = models.PositiveIntegerField("MUC (технологічний код з GLOC)", null=True, blank=True)
    create_with_claim = models.BooleanField('Створювати автоматично разом із зверненням', default=False)
    base_doc = models.BooleanField(
        'Базовий документ для формування документу звернення',
        default=False,
    )
    claim_kinds = models.ManyToManyField(ClaimKind, verbose_name='Види звернень', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тип документа"
        verbose_name_plural = "Типи документів"
        db_table = 'cl_document_kinds'


class RefusalReason(TimeStampModel):
    """Модель основания для отказа в предоставлении правовой охраны."""
    title = models.CharField("Назва", max_length=255)
    obj_kind = models.ForeignKey(
        ObjKind,
        on_delete=models.SET_NULL,
        verbose_name="Вид об'єкта промислової власності",
        null=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Підстава для відмови у наданні правової охорони"
        verbose_name_plural = "Підстави для відмови у наданні правової охорони"
        db_table = 'cl_refusal_reasons'


class Speciality(TimeStampModel):
    """Модель специальности члена АП."""
    title = models.CharField("Назва", max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Спеціальність члена АП"
        verbose_name_plural = "Спеціальністі члені АП"
        db_table = 'cl_specialities'

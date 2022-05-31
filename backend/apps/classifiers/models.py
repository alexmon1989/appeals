from django.db import models
from backend.core.models import TimeStampModel


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
    title = models.CharField("Назва", max_length=255)
    obj_kind = models.ForeignKey(
        ObjKind,
        on_delete=models.SET_NULL,
        verbose_name="Вид об'єкта промислової власності",
        null=True,
    )
    third_person = models.BooleanField("3-тя особа", default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Вид заяви/заперечення"
        verbose_name_plural = "Види заяв/заперечень"
        db_table = 'cl_claim_kinds'


class DocumentType(TimeStampModel):
    """Модель типа документа."""
    title = models.CharField("Назва", max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Тип документа"
        verbose_name_plural = "Типи документів"
        db_table = 'cl_document_kinds'


class DocumentName(TimeStampModel):
    """Модель типа документа."""
    title = models.CharField("Назва", max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Назва документа"
        verbose_name_plural = "Назви документів"
        db_table = 'cl_document_names'

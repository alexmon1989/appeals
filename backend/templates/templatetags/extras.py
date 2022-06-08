from django import template
import pathlib
import datetime


register = template.Library()


@register.filter
def filename(value):
    """Возвращает имя файла значения поля FileField."""
    return pathlib.Path(value.file.name).name


@register.filter
def to_date(value: str, fmt: str):
    d = datetime.datetime.strptime(value, fmt)
    return d

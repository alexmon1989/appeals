from django.contrib.auth import get_user_model

from ..models import Case, Document, Sign

from typing import Iterable
from pathlib import Path

UserModel = get_user_model()


def case_get_list(user: UserModel = None) -> Iterable[Case]:
    """Возвращает список апелляционных дел, к которым есть доступ у пользователя"""
    cases = Case.objects.select_related(
        'obj_kind',
        'claim_kind',
        'papers_owner',
        'expert',
        'secretary',
    ).prefetch_related(
        'collegiummembership_set__person',
        'document_set',
        'document_set__document_type',
        'document_set__document_name',
        'document_set__sign_set',
    )
    return cases


def document_get_by_id(doc_id: int, user: UserModel = None) -> Document:
    """Возвращает документ по его идентификатору."""
    document = Document.objects.filter(pk=doc_id)
    return document.first()


def sign_upload(file, dest: Path) -> bool:
    """Загружает файл с цифровой подписью на диск."""
    with open(dest, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return True


def sign_create(data: dict) -> Sign:
    """Сохраняет данные о цифровой подписи в БД."""
    sign = Sign(**data)
    sign.save()
    return sign

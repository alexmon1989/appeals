from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

from apps.cases.models import Sign, Document
from pathlib import Path
from urllib.parse import unquote


UserModel = get_user_model()


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


def sign_create_p7s(blob: InMemoryUploadedFile, document: Document, user: UserModel) -> Path:
    """Сохранение цифровой подписи на диск"""
    relative_path = Path(unquote(f"{document.file}_{user.pk}.p7s"))
    sign_destination = Path(settings.MEDIA_ROOT) / relative_path

    with open(sign_destination, 'wb+') as destination:
        for chunk in blob.chunks():
            destination.write(chunk)

    return relative_path


def sign_update(data: dict) -> Sign:
    """Обновляет данные цифровой подписи."""
    qs = Sign.objects.filter(user=data['user'], document=data['document'])
    qs.update(**data)
    return qs.first()

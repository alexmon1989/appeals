from ..models import Sign
from pathlib import Path


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

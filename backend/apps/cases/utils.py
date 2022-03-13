from pathlib import Path


def document_get_folder_path(instance) -> Path:
    """Возвращает путь к каталогу с файлами документа."""
    return Path('cases') / str(instance.case.pk) / str(instance.pk)


def document_get_original_file_path(instance, file_name: str) -> Path:
    """Возвращает путь к каталогу с файлами документа."""
    return document_get_folder_path(instance) / file_name


def sign_get_file_path(instance, file_name: str) -> Path:
    """Возвращает путь к каталогу с файлом цифровой печати."""
    return document_get_folder_path(instance.document) / file_name

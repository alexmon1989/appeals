from django.utils.datastructures import MultiValueDict
import base64
import uuid
import tempfile
from pathlib import Path


def files_to_base64(request_files: MultiValueDict) -> dict:
    """Конвертирует request.FILES в строки base64"""
    res = {}
    for key in request_files:
        res[key] = []
        files = request_files.getlist(key)
        for file in files:
            f = file.file
            file_bytes = f.read()
            file_bytes_base64 = base64.b64encode(file_bytes)
            file_bytes_base64_str = file_bytes_base64.decode('utf-8')  # this is a str
            res[key].append({'name': file.name, 'content': file_bytes_base64_str})
    return res


def base64_to_temp_file(base64_str: str) -> Path:
    """Сохраняет файл (строка base64) во временный каталог."""
    file_bytes_base64 = base64_str.encode('utf-8')
    file_bytes = base64.b64decode(file_bytes_base64)

    tmp_dir = tempfile.gettempdir()
    tmp_file_name = str(uuid.uuid4())
    tmp_file_path = Path(tmp_dir) / tmp_file_name
    with open(tmp_file_path, 'wb') as f:
        f.write(file_bytes)
    return tmp_file_path

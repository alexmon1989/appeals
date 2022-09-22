from django.conf import settings

from core.celery import app

from pathlib import Path
from urllib.parse import unquote

from apps.users import services as users_services
from .services import sign_services, document_services
from apps.common.utils import base64_to_file
from apps.filling import services as filling_services


@app.task
def upload_sign_external_task(document_id: int, sign_file_base_64: str, sign_info: dict, cert_data: dict) -> dict:
    """Создаёт на диске файл с цифровой подписью и записывает информацию о подписи в БД."""
    user = users_services.user_get_or_create_from_cert(cert_data)
    document = document_services.document_get_by_id(document_id)
    if document and document_services.document_can_be_signed_by_user(document.pk, user):
        relative_path = Path(unquote(f"{document.file}_{user.pk}.p7s"))
        sign_destination = Path(settings.MEDIA_ROOT) / relative_path
        base64_to_file(sign_file_base_64, sign_destination)
        sign_data = {
            'document': document,
            'file': str(relative_path),
            'file_signed': document.signed_file,
            'user': user,
            'subject': sign_info['subject'],
            'serial_number': sign_info['serial'],
            'issuer': sign_info['issuer'],
            'timestamp': sign_info['timestamp'],
        }
        sign_services.sign_create(sign_data)

        # Обновление статуса заявки
        filling_services.claim_set_status_if_all_docs_signed(document.claim_id)

        return {'success': 1}

    return {'success': 0}

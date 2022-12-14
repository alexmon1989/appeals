from django.conf import settings
from django.utils import timezone

from core.celery import app

from pathlib import Path
from urllib.parse import unquote
import io

from apps.users import services as users_services
from .services import sign_services, document_services
from apps.common.utils import base64_to_file
from apps.filling import services as filling_services
from apps.cases.models import Command, Sign


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

        # Запись в историю документа
        document_services.document_add_history(
            document.pk,
            f"Документ підписано КЕП (підписувач: {sign_info['subject']}, {sign_info['serial']})",
            user.pk
        )

        # Обновление статуса заявки
        filling_services.claim_set_status_if_all_docs_signed(document.claim_id)

        return {'success': 1}

    return {'success': 0}


@app.task
def handle_external_signs():
    """Получает электронные подписи из внешнего сервиса подписания и обрабатывает их."""
    # Выборка всех необработанных команд
    commands = Command.objects.filter(command_type__command_name='update_send_to_esign_service', is_done=False)

    # Обработка цифровых подписей
    for command in commands:
        for protocol in command.esignprotocolexchange_set.all():
            # Сохранение файла цифр. подписи на диск
            binary_io = io.BytesIO(protocol.esign_body)
            p7s_path = Path(protocol.doc.folder_path) / 'sign.p7s'

            with open(str(p7s_path), "wb") as f:
                f.write(binary_io.read())

            # Заполнение данных подписанта
            sign = Sign.objects.get(
                document_id=protocol.doc_id,
                user__isnull=True,
                timestamp=''
            )
            sign.timestamp = str(protocol.date_signed)
            sign.subject = protocol.signer_name
            sign.save()
            document_services.document_add_history(
                protocol.doc_id,
                'Отримано цифровий підпис від сервісу підписання документів'
            )

        command.is_done = True
        command.is_error = False
        command.execution_date = timezone.now()
        command.save()

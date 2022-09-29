from django.contrib.auth import get_user_model
from django.conf import settings

from apps.cases.models import Document, Sign, DocumentHistory
from apps.cases.utils import set_cell_border

from typing import List
from pathlib import Path
from docx import Document as DocumentWord
import random


UserModel = get_user_model()


def document_get_by_id(doc_id: int) -> Document:
    """Возвращает документ по его идентификатору."""
    doc = Document.objects.filter(pk=doc_id).prefetch_related(
        'sign_set',
        'documenthistory_set',
        'documenthistory_set__user'
    ).select_related(
        'document_type'
    )
    return doc.first()


def document_add_sign_info_to_file(doc_id: int, signs: list) -> None:
    """Создаёт .docx с инф-ей о цифровых подписях в конце (на основе оригинального файла документа)"""
    document = document_get_by_id(doc_id)

    if Path(str(document.file)).suffix == '.docx':
        # Открытие документа
        docx_file_path = Path(settings.MEDIA_ROOT) / Path(str(document.file))
        docx_with_signs_file_path = docx_file_path.parent / f"{docx_file_path.stem}_signs.docx"
        docx = DocumentWord(docx_file_path)

        # Добавление таблички с информацией о подписях
        docx.add_paragraph('Підписали:')
        table = docx.add_table(rows=len(signs), cols=1)
        for i, sign in enumerate(signs):
            cells = table.rows[i].cells
            cells[0].paragraphs[0].add_run(
                f"{sign['subject']}\n{sign['serial_number']}\n{sign['issuer']}"
            )
            paragraph_format = cells[0].paragraphs[0].paragraph_format
            paragraph_format.space_after = 0
            # set_cell_margins(cells[0], top=50, start=50, bottom=50, end=50)
            set_cell_border(
                cells[0],
                top={"sz": 12, "val": "single", "color": "black", "space": "0"},
                bottom={"sz": 12, "val": "single", "color": "black", "space": "0"},
                start={"sz": 12, "val": "single", "color": "black", "space": "0"},
                end={"sz": 12, "val": "single", "color": "black", "space": "0"},
            )

        # Сохранение
        docx.save(docx_with_signs_file_path)

    # Смена статуса обращения если все документы подписаны
    # filling_services.claim_set_status_if_all_docs_signed(document.claim_id)


def document_set_reg_number(doc_id: int) -> None:
    """Присваивает документу регистрационный номер, который возвращает глобальный нумератор."""
    numbers = ''.join([str(random.randint(0, 9)) for _ in range(5)])
    document = Document.objects.get(pk=doc_id)
    document.registration_number = f"Вх-{numbers}/2022"
    document.save()


def document_set_barcode(doc_id: int) -> None:
    """Присваивает документу штрихкод, который возвращает глобальный нумератор."""
    document = Document.objects.get(pk=doc_id)
    document.barcode = ''.join([str(random.randint(0, 9)) for _ in range(32)])
    document.save()


def document_get_signs_info(doc_id: int) -> List[dict]:
    """Возвращает информацию о подписавших документ."""
    res = []
    signs = Sign.objects.filter(
        document_id=doc_id
    ).order_by(
        'created_at'
    ).values(
        'subject',
        'serial_number',
        'issuer',
        'timestamp'
    )
    for sign in signs:
        res.append(sign)
    return res


def document_can_be_signed_by_user(document_id: int, user: UserModel) -> bool:
    """Проверяет, может ли пользователь подписывать документ."""
    document = document_get_by_id(document_id)
    if document.case:
        for sign in document.sign_set.all():
            if sign.user_id == user.pk:
                # Документ подписан пользователем
                if sign.timestamp:
                    return False
                # Документ ожидает подписания
                return True
        return False

    # Заявка (могут подписывать только заявители, которые подавали)
    return document.claim and document.claim.user_id == user.pk


def document_get_case_documents_to_sign(case_id: int, user: UserModel) -> list:
    """Возвращает список документов дела, которые ожидают подписания пользователем."""
    documents = Document.objects.filter(
        sign__user=user,
        sign__timestamp='',
        case_id=case_id
    ).order_by('-created_at')

    res = []

    for document in documents:
        res.append({
            'id': document.pk,
            'document_type': document.document_type.title,
            'auto_generated': int(document.auto_generated),
            'file_url': document.file.url,
            'file_name': Path(document.file.name).name,
        })

    return res


def document_add_history(doc_id: int, action: str, user_id: int) -> None:
    """Создаёт запись в историю дела."""
    DocumentHistory.objects.create(
        document_id=doc_id,
        action=action,
        user_id=user_id
    )

from django.contrib.auth import get_user_model
from django.conf import settings

from ..models import Case, Document, Sign
from ..utils import set_cell_border

from typing import Iterable, List
from pathlib import Path
from docx import Document as DocumentWord


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
    doc = Document.objects.filter(pk=doc_id)
    return doc.first()


def document_add_sign_info_to_file(doc_id: int) -> None:
    """Создаёт .docx с инф-ей о цифровых подписях в конце (на основе оригинального файла документа)
    и возвращает его путь."""
    document = document_get_by_id(doc_id)
    signs = document_get_signs_info(doc_id)

    if signs:
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
                f"{sign['subject']}\n{sign['serial_number']}\n{sign['issuer']}\n{sign['timestamp']}"
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

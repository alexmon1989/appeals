from django.contrib.auth import get_user_model
from django.utils.datastructures import MultiValueDict
from django.http.request import QueryDict
from django.db.models import Prefetch
from django.db.models.query import QuerySet

from ..classifiers.models import DocumentName, DocumentType
from ..cases.models import Document, Sign
from .models import ClaimField, Claim

from typing import List
import json
import datetime

UserModel = get_user_model()


def claim_create(post_data: QueryDict, files_data: MultiValueDict, user: UserModel) -> Claim:
    """Создаёт обращение пользователя."""
    stage_3_field = ClaimField.objects.filter(claim_kind=post_data['claim_kind'], stage=3).first().input_id
    claim = Claim.objects.create(
        obj_kind_id=post_data['obj_kind'],
        claim_kind_id=post_data['claim_kind'],
        third_person=post_data.get('third_person', False),
        obj_number=post_data[stage_3_field],
        json_data=json.dumps(post_data),
        user=user
    )

    # Загрузка файлов
    stage_9_fields = ClaimField.objects.filter(
        claim_kind=post_data['claim_kind'],
        stage=9,
        required=True,
        field_type__in=(ClaimField.FieldType.FILE, ClaimField.FieldType.FILE_MULTIPLE)
    )
    for field in stage_9_fields:
        # Получение имени документа
        document_name, created = DocumentName.objects.get_or_create(title=field.title)
        # Сохранение файла
        if field.field_type == ClaimField.FieldType.FILE:
            file = files_data[field.input_id]
            Document.objects.create(
                claim=claim,
                document_name=document_name,
                document_type=DocumentType.objects.filter(title='Вхідний').first(),
                input_date=datetime.datetime.now(),
                file=file
            )
        else:
            files = files_data.getlist(f"{field.input_id}[]")
            for file in files:
                Document.objects.create(
                    claim=claim,
                    document_name=document_name,
                    document_type=DocumentType.objects.filter(title='Вхідний').first(),
                    input_date=datetime.datetime.now(),
                    file=file
                )
    return claim


def claim_get_fields(bool_as_int: bool = False) -> List[ClaimField]:
    """Вовзращает возможные поля обращений (зависящие от типа)"""
    claim_fields = list(ClaimField.objects.order_by('pk').filter(enabled=True).values(
        'pk',
        'title',
        'help_text',
        'input_id',
        'field_type',
        'stage',
        'claim_kind_id',
        'editable',
        'required',
    ))
    if bool_as_int:
        for claim_field in claim_fields:
            claim_field['editable'] = int(claim_field['editable'])
            claim_field['required'] = int(claim_field['required'])

    return claim_fields


def claim_get_user_claims_qs(user: UserModel) -> QuerySet[Claim]:
    """Возвращает обращения пользователя."""
    return Claim.objects.filter(
        user=user
    ).select_related(
        'claim_kind', 'obj_kind'
    ).prefetch_related(
        'document_set', 'document_set__document_name'
    )


def claim_get_stages_details(claim: Claim) -> dict:
    """Возвращает данные заявки по этапам ввода формы."""
    fields = ClaimField.objects.filter(claim_kind=claim.claim_kind, required=True, stage__lt=9)
    stages = {
        3: {
            'title': 'Номер заявки/охоронного документа',
            'items': [],
        },
        4: {
            'title': 'Дані об\'єкта права інтелектуальної власності',
            'items': [],
        },
        5: {
            'title': 'Відомості про заявника (апелянта) та власника',
            'items': [],
        },
        6: {
            'title': 'Відомостей про апелянта (лише у випадку заперечень 3-х осіб і апеляційних заяв)',
            'items': [],
        },
        7: {
            'title': 'Додаткова інформація',
            'items': [],
        },
        8: {
            'title': 'Відомості щодо рішення Укрпатенту',
            'items': [],
        },
    }

    claim_data = json.loads(claim.json_data)
    for field in fields:
        try:
            stages[field.stage]['items'].append({
                'title': field.title,
                'value': claim_data[field.input_id],
                'type': field.field_type,
                'id': field.input_id,
            })
        except KeyError:
            pass

    return stages


def claim_get_documents_qs(claim_id: int, user_id: int) -> QuerySet[Document]:
    """Возвращает список документов обращения."""
    documents = Document.objects.filter(
        claim_id=claim_id
    ).select_related(
        'document_name'
    ).prefetch_related(
        Prefetch('sign_set', queryset=Sign.objects.filter(user_id=user_id))
    ).order_by('-auto_generated', 'pk')

    return documents

from django.contrib.auth import get_user_model
from django.utils.datastructures import MultiValueDict
from django.http.request import QueryDict
from django.db.models.query import QuerySet

from ..classifiers.models import DocumentName, DocumentType
from ..cases.models import Document
from .models import ClaimField, Claim

from typing import List
import json
import datetime

UserModel = get_user_model()


def create_claim(post_data: QueryDict, files_data: MultiValueDict, user: UserModel) -> Claim:
    """Создаёт обращение пользователя."""
    stage_3_field = ClaimField.objects.filter(claim_kind=post_data['claim_kind'], stage=3).first().input_id
    claim = Claim.objects.create(
        obj_kind_id=post_data['obj_kind'],
        claim_kind_id=post_data['claim_kind'],
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


def get_claim_fields(bool_as_int: bool = False) -> List[ClaimField]:
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


def get_users_claims_qs(user: UserModel) -> QuerySet[Claim]:
    """Возвращает обращения пользователя."""
    return Claim.objects.filter(user=user).select_related('claim_kind', 'obj_kind')

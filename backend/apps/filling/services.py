from django.contrib.auth import get_user_model
from django.utils.datastructures import MultiValueDict
from django.http.request import QueryDict
from django.db.models import Prefetch, Count, Q
from django.db.models.query import QuerySet
from django.core.files.base import ContentFile

from docx import Document as PyDocxDocument
from docx.shared import Pt
from docxcompose.composer import Composer

from ..classifiers.models import DocumentType
from ..cases.models import Document, Sign, DocumentTemplate
from .models import ClaimField, Claim
from ..common.utils import docx_replace

from typing import List, Type
from pathlib import Path
import json
import datetime
import tempfile
import uuid
import os

UserModel = get_user_model()


def claim_process_input_data(data: dict) -> dict:
    """Обрабатывает данные заявки, пришедшие от пользователя."""
    for key in data:
        if 'date' in key:
            try:
                data[key] = datetime.datetime.strptime(data[key], '%d.%m.%Y').strftime('%Y-%m-%d')
            except:
                pass
    return data


def claim_create(post_data: QueryDict, files_data: MultiValueDict, user: UserModel) -> Claim:
    """Создаёт обращение пользователя."""
    stage_3_field = ClaimField.objects.filter(claim_kind=post_data['claim_kind'], stage=3).first().input_id
    claim = Claim.objects.create(
        obj_kind_id=post_data['obj_kind'],
        claim_kind_id=post_data['claim_kind'],
        third_person=post_data.get('third_person', False),
        obj_number=post_data[stage_3_field],
        json_data=json.dumps(claim_process_input_data(post_data)),
        user=user
    )

    # Загрузка файлов
    stage_9_fields = ClaimField.objects.filter(
        claim_kind=post_data['claim_kind'],
        stage=9,
        field_type__in=(ClaimField.FieldType.FILE, ClaimField.FieldType.FILE_MULTIPLE)
    )
    for field in stage_9_fields:
        # Получение типа документа
        doc_type, created = DocumentType.objects.get_or_create(title=field.title)
        # Сохранение файла
        if field.field_type == ClaimField.FieldType.FILE:
            file = files_data[field.input_id]
            doc = Document.objects.create(
                claim=claim,
                document_type=doc_type,
                input_date=datetime.datetime.now(),
                file=file,
                claim_document=True,
            )
            if doc_type.base_doc:
                # Создание файла обращения (с шапкой)
                document_create_main_claim_doc_file(claim, doc)
        else:
            files = files_data.getlist(f"{field.input_id}[]")
            for file in files:
                Document.objects.create(
                    claim=claim,
                    document_type=doc_type,
                    input_date=datetime.datetime.now(),
                    file=file,
                    claim_document=True
                )

    return claim


def claim_edit(сlaim_id: int, post_data: dict, files_data: MultiValueDict, user: UserModel) -> Claim:
    """Редактирует обращение пользователя."""
    claim = claim_get_user_claims_qs(user).filter(pk=сlaim_id).first()

    # Удаление документов, которые указал пользователь и тех, которые генерируются автоматически
    try:
        docs_to_delete_ids = post_data['delete_doc_id']
        if type(docs_to_delete_ids) is not list:
            docs_to_delete_ids = [docs_to_delete_ids]
        del post_data['delete_doc_id']
    except KeyError:
        Document.objects.filter(claim=claim, auto_generated=True).delete()
    else:
        Document.objects.filter(Q(pk__in=docs_to_delete_ids) | Q(claim=claim, auto_generated=True)).delete()

    stage_3_field = ClaimField.objects.filter(claim_kind=post_data['claim_kind'], stage=3).first().input_id

    # Обновление текстовых данных обращения
    claim.obj_kind_id = post_data['obj_kind']
    claim.claim_kind_id = post_data['claim_kind']
    claim.third_person = post_data.get('third_person', False)
    claim.obj_number = post_data[stage_3_field]
    claim.json_data = json.dumps(claim_process_input_data(post_data))
    claim.user = user
    claim.save()

    # Загрузка файлов
    stage_9_fields = ClaimField.objects.filter(
        claim_kind=post_data['claim_kind'],
        stage=9,
        field_type__in=(ClaimField.FieldType.FILE, ClaimField.FieldType.FILE_MULTIPLE)
    )
    for field in stage_9_fields:
        if field.input_id in files_data or f"{field.input_id}[]" in files_data:
            # Получение типа документа
            doc_type, created = DocumentType.objects.get_or_create(title=field.title)
            # Сохранение файла
            if field.field_type == ClaimField.FieldType.FILE:
                # Удаление "старого" документа этого типа
                Document.objects.filter(claim=claim, document_type=doc_type).delete()
                # Загрузка нового документа
                file = files_data[field.input_id]
                Document.objects.create(
                    claim=claim,
                    document_type=doc_type,
                    input_date=datetime.datetime.now(),
                    file=file,
                    claim_document=True,
                )
            else:
                files = files_data.getlist(f"{field.input_id}[]")
                for file in files:
                    Document.objects.create(
                        claim=claim,
                        document_type=doc_type,
                        input_date=datetime.datetime.now(),
                        file=file,
                        claim_document=True
                    )

    # Формирование основного документа обращения (заявления)
    base_doc = Document.objects.filter(claim=claim, document_type__base_doc=True).first()
    if base_doc:
        document_create_main_claim_doc_file(claim, base_doc)
        claim.status = 1
        claim.save()

    return claim


def claim_get_fields(bool_as_int: bool = False) -> List[ClaimField]:
    """Вовзращает возможные поля обращений (зависящие от типа)"""
    claim_fields = list(ClaimField.objects.order_by('pk').filter(enabled=True).values(
        'pk',
        'title',
        'help_text',
        'input_id',
        'field_type',
        'allowed_extensions',
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
        'document_set', 'document_set__document_type'
    )


def claim_get_stages_details(claim: Claim) -> dict:
    """Возвращает данные заявки по этапам ввода формы."""
    fields = ClaimField.objects.filter(claim_kind=claim.claim_kind, stage__lt=9)
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
            'title': 'Відомості про заявника або власника',
            'items': [],
        },
        6: {
            'title': 'Відомості про апелянта',
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
            if claim_data[field.input_id]:
                stages[field.stage]['items'].append({
                    'title': field.title,
                    'value': claim_data[field.input_id],
                    'type': field.field_type,
                    'id': field.input_id,
                })
        except KeyError:
            pass

    if stages[3]['items'][0]['id'] == 'app_number':
        stages[5]['title'] = 'Відомості про заявника'
    else:
        stages[5]['title'] = 'Відомості про власника'

    return stages


def claim_get_documents_qs(claim_id: int, user_id: int) -> QuerySet[Document]:
    """Возвращает список документов обращения."""
    documents = Document.objects.filter(
        claim_id=claim_id,
        claim_document=True
    ).select_related(
        'document_type'
    ).prefetch_related(
        Prefetch('sign_set', queryset=Sign.objects.filter(user_id=user_id))
    ).order_by(
        '-auto_generated',
        'document_type'
    ).annotate(Count('sign'))

    return documents


def claim_get_documents(claim_id: int, user_id: int) -> list:
    """Возвращает список документов обращения в формате json."""
    documents = claim_get_documents_qs(claim_id, user_id)
    res = []
    for document in documents:
        res.append({
            'id': document.pk,
            'document_type': document.document_type.title,
            'auto_generated': int(document.auto_generated),
            'file_url': document.file.url,
            'file_name': Path(document.file.name).name,
            'sign__count': document.sign__count,
        })
    return res


def claim_set_status_if_all_docs_signed(claim_id: Type[int]) -> None:
    """Меняет статус обращения с "1" на "2" (готово к рассмотрению), если все документы подписаны пользователем."""
    try:
        claim = Claim.objects.get(pk=claim_id, status=1)
    except Claim.DoesNotExist:
        pass
    else:
        # Проверка все ли документы, поданные пользователем подписаны.
        documents = Document.objects.filter(
            claim=claim,
            claim_document=True
        ).prefetch_related(
            Prefetch(
                'sign_set',
                queryset=Sign.objects.filter(user_id=claim.user_id)
            )
        )
        for document in documents:
            # Какой-то документ не подписан
            if document.sign_set.count() == 0:
                return

        # Обновление статуса
        claim.status = 2
        claim.save()


def document_get_data_for_main_claim_doc_file(claim_id: Type[int]) -> dict:
    """Возвращает словарь с данными, необходимыми для формирования основного документа обращения."""
    claim = Claim.objects.filter(pk=claim_id).first()
    claim_data = json.loads(claim.json_data)

    res = {
        '{{ OBJ_KIND_TITLE }}': claim.claim_kind.template_title,
        '{{ OBJ_TITLE }}': claim_data['obj_title'],
        '{{ APP_NUMBER }}': claim_data['app_number'],
        '{{ APP_DATE }}': claim_data['app_date'],
        '{{ DECISION_DATE }}': claim_data.get('decision_date', ''),
        '{{ DECISION_RECEIVE_DATE }}': claim_data.get('decision_receive_date', ''),
        '{{ APPLICANT_TITLE }}': claim_data.get('applicant_title', '').replace('\r\n', '\n'),
        '{{ REGISTRATION_NUMBER }}': claim_data.get('registration_number'),
        '{{ OWNER_TITLE }}': claim_data.get('owner_title', '').replace('\r\n', '\n'),
        '{{ OWNER_ADDRESS }}': claim_data.get('owner_address', '').replace('\r\n', '\n'),
        '{{ WELL_KNOWN_DATE }}': claim_data.get('well_known_date'),
        '{{ WELL_KNOWN_CLASSES }}': claim_data.get('well_known_classes', '').replace('\r\n', '\n'),
    }

    for key in ('{{ APP_DATE }}', '{{ DECISION_DATE }}', '{{ DECISION_RECEIVE_DATE }}', '{{ WELL_KNOWN_DATE }}'):
        if res[key]:
            res[key] = datetime.datetime.strptime(res[key], '%Y-%m-%d').strftime('%d.%m.%Y')

    if claim.third_person:
        res['{{ APPELAINT_TITLE }}'] = claim_data.get('third_person_applicant_title', '').replace('\r\n', '\n')
        res['{{ APPELAINT_ADDRESS }}'] = claim_data.get('third_person_applicant_address', '').replace('\r\n', '\n')
        res['{{ REPRESENT_TITLE }}'] = claim_data.get('third_person_represent_title', '').replace('\r\n', '\n')
        res['{{ REPRESENT_ADDRESS }}'] = claim_data.get('third_person_represent_address', '').replace('\r\n', '\n')
        res['{{ MAILING_ADDRESS }}'] = claim_data.get('third_person_mailing_address', '').replace('\r\n', '\n')
        res['{{ CONTACTS_PHONE }}'] = claim_data.get('third_person_phone', '')
        res['{{ CONTACTS_EMAIL }}'] = claim_data.get('third_person_email', '')
    else:
        res['{{ APPELAINT_TITLE }}'] = claim_data.get('applicant_title', '').replace('\r\n', '\n') \
                                       or claim_data.get('owner_title', '').replace('\r\n', '\n')
        res['{{ APPELAINT_ADDRESS }}'] = claim_data.get('applicant_address', '').replace('\r\n', '\n') \
                                         or claim_data.get('owner_address', '').replace('\r\n', '\n')
        res['{{ REPRESENT_TITLE }}'] = claim_data.get('represent_title', '').replace('\r\n', '\n')
        res['{{ REPRESENT_ADDRESS }}'] = claim_data.get('represent_address', '').replace('\r\n', '\n')
        res['{{ MAILING_ADDRESS }}'] = claim_data.get('mailing_address', '').replace('\r\n', '\n')
        res['{{ CONTACTS_PHONE }}'] = claim_data.get('phone', '')
        res['{{ CONTACTS_EMAIL }}'] = claim_data.get('email', '')

    return res


def document_create_main_claim_doc_file(claim: Claim, base_doc: Document) -> Document:
    """Создаёт документ файл обращения."""
    doc_type = DocumentType.objects.filter(claim_kinds__id=claim.claim_kind.pk, create_with_claim=True).first()
    if doc_type:
        doc_template = DocumentTemplate.objects.filter(documents_types__code=doc_type.code).first()
        doc_header = PyDocxDocument(doc_template.file.file)

        doc_data_to_replace = document_get_data_for_main_claim_doc_file(claim.pk)
        docx_replace(doc_header, doc_data_to_replace)

        tmp_dir = tempfile.gettempdir()
        tmp_file_name = f'{uuid.uuid4()}.docx'
        tmp_file_path = Path(tmp_dir) / tmp_file_name

        doc_header.save(tmp_file_path)

        master = doc_header
        composer = Composer(master)
        doc_body = PyDocxDocument(base_doc.file)
        composer.append(doc_body)
        composer.save(tmp_file_path)

        # Поставить всему документу 12-й размер шрифта и Times New Roman
        input_doc = PyDocxDocument(tmp_file_path)
        for paragraph in input_doc.paragraphs:
            paragraph.style = input_doc.styles['Normal']
            for run in paragraph.runs:
                run.font.name = 'Times New Roman'
                run.font.size = Pt(12)
        input_doc.save(tmp_file_path)

        doc = Document.objects.create(
            claim=claim,
            document_type=doc_type,
            input_date=datetime.datetime.now(),
            claim_document=True,
            auto_generated=1
        )

        with open(tmp_file_path, "rb") as fh:
            with ContentFile(fh.read()) as file_content:
                doc.file.save(tmp_file_name, file_content)
                doc.save()

        os.remove(tmp_file_path)

        return doc

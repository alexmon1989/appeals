from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..classifiers.models import ObjKind, ClaimKind, DocumentName, DocumentType
from .models import ClaimField, Claim
from ..cases.models import Document

import json
import datetime


@login_required
def my_applications_list(request):
    """Отображает страницу со списком апелляционных дел."""
    return render(request, 'filling/my_applications_list/index.html')


@login_required
def create_application(request):
    """Отображает страницу со формой создания обращения."""
    if request.method == 'POST':
        stage_3_field = ClaimField.objects.filter(claim_kind=request.POST['claim_kind'], stage=3).first().input_id

        json_data = request.POST.dict()
        del json_data['csrfmiddlewaretoken']
        json_data = json.dumps(json_data)

        claim = Claim.objects.create(
            obj_kind_id=request.POST['obj_kind'],
            claim_kind_id=request.POST['claim_kind'],
            obj_number=request.POST[stage_3_field],
            json_data=json_data,
            user=request.user
        )

        # Загрузка файлов
        stage_9_fields = ClaimField.objects.filter(
            claim_kind=request.POST['claim_kind'],
            stage=9,
            required=True,
            field_type__in=(ClaimField.FieldType.FILE, ClaimField.FieldType.FILE_MULTIPLE)
        )
        for field in stage_9_fields:
            # Получение имени документа
            document_name, created = DocumentName.objects.get_or_create(title=field.title)
            # Сохранение файла
            if field.field_type == ClaimField.FieldType.FILE:
                file = request.FILES[field.input_id]
                Document.objects.create(
                    claim=claim,
                    document_name=document_name,
                    document_type=DocumentType.objects.filter(title='Вхідний').first(),
                    input_date=datetime.datetime.now(),
                    file=file
                )
            else:
                files = request.FILES.getlist(f"{field.input_id}[]")
                for file in files:
                    Document.objects.create(
                        claim=claim,
                        document_name=document_name,
                        document_type=DocumentType.objects.filter(title='Вхідний').first(),
                        input_date=datetime.datetime.now(),
                        file=file
                    )
        return JsonResponse({'success': 1, 'claim_id': claim.pk})

    # Типы объектов
    obj_kinds = list(ObjKind.objects.order_by('pk').values('pk', 'title', 'sis_id'))

    # Типы обращений
    claim_kinds = list(ClaimKind.objects.order_by('pk').values('pk', 'title', 'obj_kind_id', 'third_person'))
    for claim_kind in claim_kinds:
        claim_kind['third_person'] = int(claim_kind['third_person'])

    # Возможные поля обращений (зависящие от типа)
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
    for claim_field in claim_fields:
        claim_field['editable'] = int(claim_field['editable'])
        claim_field['required'] = int(claim_field['required'])

    return render(
        request,
        'filling/create_application/index.html',
        {
            'obj_kinds': obj_kinds,
            'claim_kinds': claim_kinds,
            'claim_fields': claim_fields,
        }
    )

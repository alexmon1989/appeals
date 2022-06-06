from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..classifiers.models import ObjKind, ClaimKind
from .models import ClaimField


@login_required
def my_applications_list(request):
    """Отображает страницу со списком апелляционных дел."""
    return render(request, 'filling/my_applications_list/index.html')


@login_required
def create_application(request):
    """Отображает страницу со формой создания обращения."""
    if request.method == 'POST':
        print(request.POST)
        print(request.FILES)
        return JsonResponse({'success': 1})


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

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..classifiers import services as classifiers_services
from . import services as filling_services


@login_required
def my_applications_list(request):
    """Отображает страницу со списком апелляционных дел."""
    claims = filling_services.get_users_claims_qs(request.user)
    return render(request, 'filling/my_applications_list/index.html', {'claims': claims})


@login_required
def create_application(request):
    """Отображает страницу со формой создания обращения."""

    # Создание заявки если был POST-запрос
    if request.method == 'POST':
        post_data = request.POST.dict()
        del post_data['csrfmiddlewaretoken']
        claim = filling_services.create_claim(post_data, request.FILES, request.user)
        return JsonResponse({'success': 1, 'claim_id': claim.pk})

    # Типы объектов
    obj_kinds = classifiers_services.get_obj_kinds_list()

    # Типы обращений
    claim_kinds = classifiers_services.get_claim_kinds(bool_as_int=True)

    # Возможные поля обращений (зависящие от типа)
    claim_fields = filling_services.get_claim_fields(bool_as_int=True)

    return render(
        request,
        'filling/create_application/index.html',
        {
            'obj_kinds': obj_kinds,
            'claim_kinds': claim_kinds,
            'claim_fields': claim_fields,
        }
    )

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings

from celery.result import AsyncResult

from apps.common.mixins import LoginRequiredMixin
from apps.common.utils import qdict_to_dict
from apps.users import services as users_services
from .tasks import (get_app_data_from_es_task, get_filling_form_data_task, create_claim_task,
                    create_claim_task_internal, get_claim_data_task, get_claim_data_task_internal, edit_claim_task,
                    edit_claim_task_internal, delete_claim_task, delete_claim_task_internal, create_case_task,
                    create_case_task_internal, get_claim_status, get_claim_list_task, create_files_with_signs_info_task)
from apps.common.utils import files_to_base64

import json


class MyClaimsListView(LoginRequiredMixin, TemplateView):
    """Отображает страницу со списком обращений."""
    template_name = 'filling/my_claims_list/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = get_claim_list_task.delay(
            users_services.certificate_get_data(self.request.session['cert_id'])
        )
        context['task_id'] = task.id
        return context


class CreateClaimView(LoginRequiredMixin, View):
    """Отображает страницу создания обращения."""
    template_name = 'filling/create_claim/index.html'
    internal_claim = settings.AUTH_METHOD == 'common'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'internal_claim': self.internal_claim})

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, создаёт обращение (задачу на создание)."""
        post_data = request.POST.dict()
        del post_data['csrfmiddlewaretoken']

        if self.internal_claim:
            task = create_claim_task_internal.delay(
                post_data,
                files_to_base64(request.FILES),
                request.user.pk,
            )
        else:
            task = create_claim_task.delay(
                post_data,
                files_to_base64(request.FILES),
                users_services.certificate_get_data(self.request.session['cert_id'])
            )

        return JsonResponse(
            {
                "task_id": task.id,
            }
        )


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ClaimDetailView(LoginRequiredMixin, TemplateView):
    """Отображает страницу с данными обращения."""
    template_name = 'filling/claim_detail/index.html'
    internal_claim = settings.AUTH_METHOD == 'common'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.internal_claim:
            task = get_claim_data_task_internal.delay(
                kwargs['pk'],
                self.request.user.pk,
            )
        else:
            task = get_claim_data_task.delay(
                kwargs['pk'],
                users_services.certificate_get_data(self.request.session['cert_id'])
            )
        context['task_id'] = task.id
        context['internal_claim'] = self.internal_claim
        return context


@login_required
def claim_status(request, pk):
    """Возвращает статус заявки в формате JSON."""
    task = get_claim_status.delay(
        pk,
        users_services.certificate_get_data(request.session['cert_id'])
    )

    return JsonResponse(
        {
            "task_id": task.id
        }
    )


@login_required
def claim_delete(request, pk):
    """Удаление обращения."""
    internal_claim = settings.AUTH_METHOD == 'common'
    if internal_claim:
        task = delete_claim_task_internal.delay(pk, request.user.pk)
    else:
        task = delete_claim_task.delay(
            pk,
            users_services.certificate_get_data(request.session['cert_id'])
        )

    return JsonResponse(
        {
            "task_id": task.id,
        }
    )


class ClaimUpdateView(LoginRequiredMixin, View):
    """Отображает страницу редактирвоания обращения."""
    template_name = 'filling/update_claim/index.html'
    internal_claim = settings.AUTH_METHOD == 'common'

    def get(self, request, *args, **kwargs):
        if self.internal_claim:
            task = get_claim_data_task_internal.delay(
                kwargs['pk'],
                request.user.pk,
                status__lt=3
            )
        else:
            task = get_claim_data_task.delay(
                kwargs['pk'],
                users_services.certificate_get_data(self.request.session['cert_id']),
                status__lt=3
            )

        return render(
            request,
            self.template_name,
            {
                'task_id': task.id,
                'internal_claim': self.internal_claim,
            }
        )

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, редактирует обращение."""
        post_data = qdict_to_dict(request.POST)
        del post_data['csrfmiddlewaretoken']

        if self.internal_claim:
            task = edit_claim_task_internal.delay(
                self.kwargs['pk'],
                post_data,
                files_to_base64(request.FILES),
                request.user.pk,
            )
        else:
            task = edit_claim_task.delay(
                self.kwargs['pk'],
                post_data,
                files_to_base64(request.FILES),
                users_services.certificate_get_data(self.request.session['cert_id'])
            )

        return JsonResponse({'task_id': task.id})


@login_required
def case_create(request, claim_id):
    """Создаёт дело на основе обращения."""
    internal_claim = settings.AUTH_METHOD == 'common'
    if internal_claim:
        task = create_case_task_internal.delay(
            claim_id,
            request.user.id
        )
    else:
        task = create_case_task.delay(
            claim_id,
            users_services.certificate_get_data(request.session['cert_id'])
        )

    return JsonResponse({'task_id': task.id})


@login_required
def get_data_from_sis(request):
    """Создаёт задачу на получение данных из СИС по объекту."""
    try:
        obj_num_type = request.GET['obj_num_type']
        obj_number = request.GET['obj_number']
        obj_kind_id_sis = int(request.GET['obj_kind_id_sis'])
        obj_state = int(request.GET['obj_state'])
    except KeyError:
        return HttpResponseBadRequest('Wrong request parameters.')

    internal_user = settings.AUTH_METHOD == 'common'

    # Имена пользователя из сертификата эцп
    if not internal_user:
        user_names = list(set(users_services.certificate_get_user_names(request.session['cert_id'])))
    else:
        user_names = None

    # Создание асинхронной задачи для Celery
    task = get_app_data_from_es_task.delay(
        obj_num_type,
        obj_number,
        obj_kind_id_sis,
        obj_state,
        user_names,
        internal_user,
    )

    return JsonResponse(
        {
            "task_id": task.id,
        }
    )


@login_required
def get_task_result(request, task_id: str):
    """Возвращает JSON с результатами выполнения задачи."""
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return JsonResponse(result)


@login_required
def get_filling_form_data(request):
    """Создаёт задачу на получение данных для формы подачи обращения."""
    task = get_filling_form_data_task.delay()
    return JsonResponse(
        {
            "task_id": task.id,
        }
    )


@login_required
def set_message(request, level, message):
    """Добавляет сообщение Django."""
    message_level = messages.INFO
    if level == 'success':
        message_level = messages.SUCCESS
    elif level == 'danger':
        message_level = messages.ERROR
    elif level == 'warning':
        message_level = messages.WARNING

    messages.add_message(
        request,
        message_level,
        message
    )

    return JsonResponse({'success': 1})


@require_POST
@login_required
def create_files_with_signs_info(request, claim_id):
    """Создаёт файлы с информацией о подписи."""
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    signs = [{
        'subject': body['subjCN'],
        'issuer': body['issuerCN'],
        'serial_number': body['serial'],
    }]

    task = create_files_with_signs_info_task.delay(
        users_services.certificate_get_data(request.session['cert_id']),
        claim_id,
        signs,
    )
    return JsonResponse(
        {
            "task_id": task.id,
        }
    )


@csrf_exempt
def test_upload(request):
    return render(request, 'filling/test_upload.html', {'files': request.FILES})

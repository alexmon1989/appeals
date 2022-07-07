from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse, Http404, HttpResponseBadRequest
from django.views import View
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from celery.result import AsyncResult

from . import services as filling_services
from ..common.mixins import LoginRequiredMixin
from ..common.utils import qdict_to_dict
from .models import Claim
from ..cases.services import services as case_services
from ..users import services as users_services
from .tasks import (get_app_data_from_es_task, get_filling_form_data_task, create_claim_task, get_claim_data_task,
                    edit_claim_task, delete_claim_task)
from .utils import files_to_base64


class MyClaimsListView(LoginRequiredMixin, ListView):
    """Отображает страницу со списком обращений."""
    model = Claim
    template_name = 'filling/my_claims_list/index.html'
    context_object_name = 'claims'

    def get_queryset(self):
        return filling_services.claim_get_user_claims_qs(self.request.user)


class CreateClaimView(LoginRequiredMixin, View):
    """Отображает страницу создания обращения."""

    template_name = 'filling/create_claim/index.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, создаёт обращение (задачу на создание)."""
        post_data = request.POST.dict()
        del post_data['csrfmiddlewaretoken']

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = get_claim_data_task.delay(
            kwargs['pk'],
            users_services.certificate_get_data(self.request.session['cert_id'])
        )
        context['task_id'] = task.id
        return context


@login_required
def claim_status(request, pk):
    """Возвращает статус заявки в формате JSON."""
    claim = filling_services.claim_get_user_claims_qs(request.user).filter(pk=pk).first()
    if claim:
        return JsonResponse({
            'success': 1,
            'data': {
                'status_code': claim.status,
                'status_verbal': claim.get_status_display()
            }
        })
    return JsonResponse({'success': 0})


@login_required
def claim_delete(request, pk):
    """Удаление обращения."""
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

    def get(self, request, *args, **kwargs):
        task = get_claim_data_task.delay(
            kwargs['pk'],
            users_services.certificate_get_data(self.request.session['cert_id']),
            status__lt=3
        )

        return render(
            request,
            self.template_name,
            {
                'task_id': task.id
            }
        )

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, редактирует обращение."""
        post_data = qdict_to_dict(request.POST)
        del post_data['csrfmiddlewaretoken']

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
    case = case_services.case_create_from_claim(claim_id, request.user)
    if case:
        messages.add_message(
            request,
            messages.SUCCESS,
            f'Справу {case.case_number} успішно створено.'
        )
        return JsonResponse({'url': reverse('claim_detail', kwargs={'pk': claim_id})})
    else:
        return HttpResponseBadRequest('Ви не можете передати звернення, тому що документи не було підписано.')


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

    # Имена пользователя из сертификата эцп
    user_names = list(set(users_services.certificate_get_user_names(request.session['cert_id'])))

    # Создание асинхронной задачи для Celery
    task = get_app_data_from_es_task.delay(
        obj_num_type,
        obj_number,
        obj_kind_id_sis,
        obj_state,
        user_names,
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

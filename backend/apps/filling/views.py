from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404, HttpResponseBadRequest
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from ..classifiers import services as classifiers_services
from . import services as filling_services
from ..common.mixins import LoginRequiredMixin
from ..common.utils import qdict_to_dict
from .models import Claim
from ..cases.services import services as case_services


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
        # Типы объектов
        obj_kinds = classifiers_services.get_obj_kinds_list()

        # Типы обращений
        claim_kinds = classifiers_services.get_claim_kinds(bool_as_int=True)

        # Возможные поля обращений (зависящие от типа)
        claim_fields = filling_services.claim_get_fields(bool_as_int=True)

        return render(
            request,
            self.template_name,
            {
                'obj_kinds': obj_kinds,
                'claim_kinds': claim_kinds,
                'claim_fields': claim_fields,
            }
        )

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, создаёт обращение."""
        post_data = request.POST.dict()
        del post_data['csrfmiddlewaretoken']

        claim = filling_services.claim_create(post_data, request.FILES, request.user)
        messages.add_message(
            request,
            messages.SUCCESS,
            'Звернення успішно створено. Будь ласка, перевірте дані та підпишіть додатки за допомогою КЕП.'
        )

        return JsonResponse({'success': 1, 'claim_url': claim.get_absolute_url()})


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ClaimDetailView(LoginRequiredMixin, DetailView):
    """Отображает страницу с данными обращения."""
    model = Claim
    template_name = 'filling/claim_detail/index.html'

    def get_queryset(self):
        return filling_services.claim_get_user_claims_qs(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stages'] = filling_services.claim_get_stages_details(self.object)
        context['documents'] = filling_services.claim_get_documents(self.object.pk, self.request.user.pk)
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
    claim = filling_services.claim_get_user_claims_qs(request.user).filter(pk=pk, status__lt=3).first()
    if claim:
        claim.delete()
        messages.add_message(
            request,
            messages.SUCCESS,
            'Звернення успішно видалено.'
        )
        return redirect('my-claims-list')
    raise Http404()


class ClaimUpdateView(LoginRequiredMixin, View):
    """Отображает страницу редактирвоания обращения."""

    template_name = 'filling/update_claim/index.html'

    def get(self, request, *args, **kwargs):
        # Данные заявки
        claim = filling_services.claim_get_user_claims_qs(request.user).filter(pk=self.kwargs['pk'], status__lt=3).first()
        stages = filling_services.claim_get_stages_details(claim)
        documents = filling_services.claim_get_documents(claim.pk, self.request.user.pk)

        initial_data = {
            'obj_kind_id': claim.obj_kind.id,
            'claim_kind_id': claim.claim_kind.id,
            'stages_data': stages,
            'documents': documents,
        }

        # Типы объектов
        obj_kinds = classifiers_services.get_obj_kinds_list()

        # Типы обращений
        claim_kinds = classifiers_services.get_claim_kinds(bool_as_int=True)

        # Возможные поля обращений (зависящие от типа)
        claim_fields = filling_services.claim_get_fields(bool_as_int=True)

        return render(
            request,
            self.template_name,
            {
                'claim': claim,
                'initial_data': initial_data,
                'obj_kinds': obj_kinds,
                'claim_kinds': claim_kinds,
                'claim_fields': claim_fields,
            }
        )

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, редактирует обращение."""

        post_data = qdict_to_dict(request.POST)
        del post_data['csrfmiddlewaretoken']

        claim = filling_services.claim_edit(self.kwargs['pk'], post_data, request.FILES, request.user)
        messages.add_message(
            request,
            messages.SUCCESS,
            'Звернення успішно відредаговано. Будь ласка, перевірте дані та підпишіть додатки за допомогою КЕП.'
        )

        return JsonResponse({'success': 1, 'claim_url': claim.get_absolute_url()})


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
        return redirect('claim_detail', pk=claim_id)
    else:
        return HttpResponseBadRequest('Ви не можете передати звернення, тому що документи не було підписано.')

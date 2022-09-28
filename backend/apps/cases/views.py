import json

from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from rest_framework import viewsets

from apps.users import services as users_services
from apps.common.utils import files_to_base64
from apps.common.decorators import group_required

from .services import case_services, document_services, sign_services, case_stage_step_change_action_service
from apps.notifications.services import AlertNotifier, UsersDbNotifier
from apps.filling import services as filling_services
from .models import Case
from .permissions import HasAccessToCase
from .serializers import DocumentSerializer, CaseSerializer, CaseHistorySerializer
from apps.common.mixins import LoginRequiredMixin
from .tasks import upload_sign_external_task
from .forms import CaseUpdateForm, CaseCreateCollegiumForm
from apps.classifiers import services as classifiers_services


@login_required
def cases_list(request):
    """Отображает страницу со списком апелляционных дел."""
    obj_kinds = classifiers_services.get_obj_kinds_list()
    return render(request, 'cases/list/index.html', {'obj_kinds': obj_kinds})


class CasesViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает JSON с документами дела."""
    serializer_class = CaseSerializer

    def get_queryset(self):
        all_cases = case_services.case_get_all_qs()
        return case_services.case_filter_dt_list(
            all_cases,
            self.request.user.id,
            self.request.GET.get('user'),
            self.request.GET.get('objKind'),
            self.request.GET.get('stage'),
        )


class CaseDetailView(LoginRequiredMixin, DetailView):
    """Отображает страницу апелляционного дела."""
    model = Case
    template_name = 'cases/detail/index.html'

    def get_queryset(self):
        return case_services.case_get_all_qs()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stages'] = case_services.case_get_stages(self.object.pk)
        context['claim'] = filling_services.claim_get_data_by_id(self.object.claim.pk)
        # Документы, которые должен подписать пользователь
        context['documents_to_sign'] = document_services.document_get_case_documents_to_sign(
            self.object.pk, self.request.user
        )
        return context


@method_decorator(group_required('Секретар'), name='dispatch')
class CaseUpdateView(LoginRequiredMixin, UpdateView):
    """Отображает страницу обновления данных дела."""
    model = Case
    form_class = CaseUpdateForm
    template_name = 'cases/update/index.html'

    def get_queryset(self):
        return case_services.case_get_all_qs().filter(secretary=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        if self.request.POST.get('goto_2001'):
            return reverse_lazy('cases-detail', kwargs={'pk': self.kwargs['pk']})
        return reverse_lazy('cases_update', kwargs={'pk': self.kwargs['pk']})


@login_required
@group_required('Секретар')
def take_to_work(request, pk: int):
    """Принимает дело в работу и переадресовывает на страницу деталей дела."""
    # Проверка какому стадии соответствует дело, смена стадии, выполнение сопутствующих стадии операций
    case = case_services.case_get_one(pk)
    current_user_notifiers = (
        AlertNotifier(request),
    )
    multiple_user_notifiers = (
        UsersDbNotifier(),
    )
    stage_set_service = case_stage_step_change_action_service.CaseSetActualStageStepService(
        case_stage_step_change_action_service.CaseStageStepQualifier(),
        case,
        request.user,
        current_user_notifiers,
        multiple_user_notifiers
    )
    if stage_set_service.execute():
        return redirect('cases-detail', pk=pk)
    raise Http404()


@require_POST
@login_required
def upload_sign_external(request, document_id: int):
    """Загружает на сервер информацию о цифровой подписи документа."""
    files_base64 = files_to_base64(request.FILES)

    task = upload_sign_external_task.delay(
        document_id,
        files_base64['blob'][0]['content'],
        json.loads(request.POST['sign_info']),
        users_services.certificate_get_data(request.session['cert_id']),
    )
    return JsonResponse(
        {
            "task_id": task.id,
        }
    )


def upload_sign_internal(request, document_id: int):
    """Загружает цифровую подпись на диск и создаёт запись в БД."""
    document = document_services.document_get_by_id(document_id)
    # Может ли пользователь подписывать файл
    if document_services.document_can_be_signed_by_user(document.pk, request.user):
        # Сохранение цифровой подписи на диск
        relative_path = sign_services.sign_create_p7s(request.FILES['blob'], document, request.user)

        # Создание записи в БД
        sign_info = json.loads(request.POST['sign_info'])
        sign_data = {
            'document': document,
            'file': str(relative_path),
            'file_signed': document.signed_file,
            'user': request.user,
            'subject': sign_info['subject'],
            'serial_number': sign_info['serial'],
            'issuer': sign_info['issuer'],
            'timestamp': sign_info['timestamp'],
        }
        sign_services.sign_update(sign_data)

        # Проверка какому стадии соответствует дело, смена стадии, выполнение сопутствующих стадии операций
        current_user_notifiers = (
            AlertNotifier(request),
            # UsersDbNotifier([request.user])
        )
        multiple_user_notifiers = (
            UsersDbNotifier(),
        )
        case_stage_step_change_action_service.CaseSetActualStageStepService(
            case_stage_step_change_action_service.CaseStageStepQualifier(),
            document.case,
            request.user,
            current_user_notifiers,
            multiple_user_notifiers
        ).execute()

        return JsonResponse(
            {
                "success": 1,
            }
        )
    else:
        return JsonResponse(
            {
                "error": 1,
                "message": "Ви не можете підписувати цей файл."
            },
            status=400
        )


class DocumentsViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает JSON с документами дела."""
    serializer_class = DocumentSerializer
    permission_classes = (HasAccessToCase,)

    def get_queryset(self):
        return case_services.case_get_documents_qs(self.kwargs['id'])


class CaseHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает JSON с документами дела."""
    serializer_class = CaseHistorySerializer
    permission_classes = (HasAccessToCase,)

    def get_queryset(self):
        return case_services.case_get_history(self.kwargs['id'])


def document_signs_info(request, document_id: int):
    """Отображает информацию о цифровых подписях документа."""
    document = document_services.document_get_by_id(document_id)
    return render(request, 'cases/detail/document_signs_info.html', {'document': document})


@method_decorator(group_required('Секретар'), name='dispatch')
class CaseCreateCollegium(LoginRequiredMixin, UpdateView):
    """Отображает страницу создания коллегии."""
    model = Case
    form_class = CaseCreateCollegiumForm
    template_name = 'cases/create_collegium/index.html'

    def get_queryset(self):
        return case_services.case_get_all_qs().filter(secretary=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse_lazy('cases-detail', kwargs={'pk': self.kwargs['pk']})


@require_POST
@login_required
def create_files_with_signs_info(request, case_id):
    """Создаёт файлы документов (которые должен подписать пользователь) с информацией о подписи внизу файла."""
    # Данные подписи из запроса
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    signs = [{
        'subject': body['subjCN'],
        'issuer': body['issuerCN'],
        'serial_number': body['serial'],
    }]

    # Документы на подпись
    documents = document_services.document_get_case_documents_to_sign(
        case_id, request.user
    )

    # Создание файлов с информацией о подписях
    for document in documents:
        # Может ли пользователь подписывать файл
        if document_services.document_can_be_signed_by_user(document['id'], request.user):
            document_services.document_add_sign_info_to_file(document['id'], signs)
        else:
            return JsonResponse(
                {
                    "error": 1,
                    "message": "Ви не можете підписати файл."
                },
                status=400
            )

    return JsonResponse(
        {
            "success": 1
        }
    )


@xframe_options_exempt
def ds_file(request):
    return render(request, template_name='cases/digital_sign/file.html')


@xframe_options_exempt
def ds_token(request):
    return render(request, template_name='cases/digital_sign/token.html')


def ds_iframe(request):
    return render(request, template_name='cases/digital_sign/iframe.html')


def decisions(request, date):
    return JsonResponse([
        {
            'obj_type': 6,
            'decision_date': '2022-08-01',
            'decision_file': '/media/publications/0001_2022/decision.pdf',
            'order_file': '/media/publications/0001_2022/order.pdf',
            'obj_title': 'cmapto, смарто',
            'tm_image': '/media/publications/0001_2022/image.jpg',
        },
        {
            'obj_type': 4,
            'decision_date': '2022-08-01',
            'decision_file': '/media/publications/0004_2022/decision.pdf',
            'order_file': '/media/publications/0004_2022/order.pdf',
            'obj_title': 'ЕТИКЕТКА',
        },
    ], safe=False)

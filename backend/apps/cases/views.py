import json

from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib import messages

from rest_framework import viewsets

from apps.users import services as users_services
from apps.common.utils import files_to_base64
from apps.common.decorators import group_required

from .services import case_services, document_services, sign_services, case_stage_step_change_action_service
from apps.filling import services as filling_services
from .models import Case, Document
from .permissions import HasAccessToCase
from .serializers import DocumentSerializer, CaseSerializer, CaseHistorySerializer
from apps.common.mixins import LoginRequiredMixin
from .tasks import upload_sign_external_task
from .forms import (CaseUpdateForm, CaseCreateCollegiumForm, CaseAcceptForConsiderationForm, DocumentAddForm,
                    DocumentUpdateForm, CasePausingForm, CaseStoppingForm, CaseMeetingForm)
from apps.classifiers import services as classifiers_services
from apps.notifications.services import Service as NotificationService, DbChannel


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
            self.request.GET.get('users'),
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
        context['case_has_unsigned_docs'] = self.object.has_unsigned_docs
        return context


@method_decorator(group_required('Секретар'), name='dispatch')
class CaseUpdateView(UpdateView):
    """Отображает страницу обновления данных дела."""
    model = Case
    form_class = CaseUpdateForm
    template_name = 'cases/update/index.html'

    def get_queryset(self):
        return case_services.case_get_all_active_qs().filter(secretary=self.request.user, stage_step__code__gte=2000)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        if self.request.POST.get('goto_2001'):
            return reverse_lazy('cases-detail', kwargs={'pk': self.kwargs['pk']})
        return reverse_lazy('cases_update', kwargs={'pk': self.kwargs['pk']})


@group_required('Секретар')
def take_to_work(request, pk: int):
    """Принимает дело в работу и переадресовывает на страницу деталей дела."""
    # Проверка какому стадии соответствует дело, смена стадии, выполнение сопутствующих стадии операций
    case = case_services.case_get_one(pk)
    stage_set_service = case_stage_step_change_action_service.CaseSetActualStageStepService(
        case_stage_step_change_action_service.CaseStageStepQualifier(),
        case,
        request,
        NotificationService([DbChannel()])
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
        document_services.document_add_history(
            document.pk,
            f"Документ підписано КЕП (підписувач: {sign_info['subject']}, {sign_info['serial']})",
            request.user.pk
        )

        # Проверка какому стадии соответствует дело, смена стадии, выполнение сопутствующих стадии операций
        stage_set_service = case_stage_step_change_action_service.CaseSetActualStageStepService(
            case_stage_step_change_action_service.CaseStageStepQualifier(),
            document.case,
            request,
            NotificationService([DbChannel()])
        )
        stage_set_service.execute()

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


def case_renew_consideration(request, pk: int):
    """Возобновляет рассмотрение ап. дела."""
    case_services.case_renew_consideration(pk, request.user.pk)
    return redirect('cases-detail', pk=pk)


def document_signs_info(request, document_id: int):
    """Отображает информацию о цифровых подписях документа."""
    document = document_services.document_get_by_id(document_id)
    return render(request, 'cases/detail/document_signs_info.html', {'document': document})


def document_history(request, document_id: int):
    """Отображает информацию о цифровых подписях документа."""
    document = document_services.document_get_by_id(document_id)
    return render(request, 'cases/detail/document_history.html', {'document': document})


@method_decorator(group_required('Секретар'), name='dispatch')
class CaseCreateCollegium(UpdateView):
    """Отображает страницу создания коллегии."""
    model = Case
    form_class = CaseCreateCollegiumForm
    template_name = 'cases/create_collegium/index.html'

    def get_queryset(self):
        return case_services.case_get_all_qs().filter(secretary=self.request.user, stage_step__code=2001)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse_lazy('cases-detail', kwargs={'pk': self.kwargs['pk']})


@method_decorator(group_required('Секретар'), name='dispatch')
class CaseConsiderForAcceptance(UpdateView):
    """Отображает страницу принятия дела к рассмотрению."""
    model = Case
    form_class = CaseAcceptForConsiderationForm
    template_name = 'cases/consider_for_acceptance/index.html'

    def get_queryset(self):
        # Функция доступна только на стадии 2003 "Розпорядження підписано. Очікує на прийняття до розгляду."
        return case_services.case_get_all_qs().filter(
            secretary=self.request.user,
            stage_step__code=2003,
            stopped=False,
            paused=False
        ).exclude(document__sign__timestamp='')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse_lazy('cases-detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Типы документов, которые будут сгенерированы
        context['docs_to_generate'] = classifiers_services.get_doc_types_for_consideration(
            self.object.claim.claim_kind_id
        )
        # Проверка все ли типы документов присутствуют
        context['templates_missed'] = any([not x['template'] for x in context['docs_to_generate']])

        return context


@method_decorator(group_required('Секретар'), name='dispatch')
class CasePausingView(UpdateView):
    """Отображает страницу остановки рассмотрения дела."""
    model = Case
    form_class = CasePausingForm
    template_name = 'cases/pausing/index.html'

    def get_queryset(self):
        # Функция доступна когда сформирована коллегия
        return case_services.case_get_all_qs().filter(
            secretary=self.request.user,
            stage_step__code__gte=2003,
            paused=False,
            stopped=False
        ).exclude(document__sign__timestamp='')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['doc_types'] = classifiers_services.get_doc_types_for_pausing(
            self.object.claim.claim_kind_id
        )
        return kwargs

    def get_success_url(self):
        return reverse_lazy('cases-detail', kwargs={'pk': self.kwargs['pk']})


@method_decorator(group_required('Секретар'), name='dispatch')
class CaseStoppingView(UpdateView):
    """Отображает страницу остановки рассмотрения дела."""
    model = Case
    form_class = CaseStoppingForm
    template_name = 'cases/stopping/index.html'

    def get_queryset(self):
        # Функция доступна когда сформирована коллегия
        return case_services.case_get_all_qs().filter(
            secretary=self.request.user,
            paused=False,
            stopped=False
        ).exclude(document__sign__timestamp='')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['doc_types'] = classifiers_services.get_doc_types_for_stopping(
            self.object.claim.claim_kind_id
        )
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
            document_services.document_add_sign_info_to_file(document['id'], signs, True, request.user.pk)
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


@group_required('Секретар')
def case_create_pre_meeting_protocol(request, pk: int):
    """Создаёт документ протокола о предварительном заседании."""
    # Получение дела
    case = case_services.case_get_all_qs().filter(
        secretary=request.user,
        stopped=False,
        paused=False,
        stage_step__code=2005,
        pk=pk
    ).first()
    if not case:
        raise Http404

    # Создание документа
    case_services.case_create_docs(
        case_id=case.pk,
        doc_types_codes=['0027'],
        user_id=request.user.pk
    )

    # Сообщение об успехе
    messages.add_message(request, messages.SUCCESS, 'Документ успішно створено та додано до справи.')

    # Переадресация на страницу дела
    return redirect('cases-detail', pk=pk)


@method_decorator(group_required('Секретар'), name='dispatch')
class CaseMeetingView(UpdateView):
    """Отображает страницу проведения дела."""
    model = Case
    form_class = CaseMeetingForm
    template_name = 'cases/meeting/index.html'

    def get_queryset(self):
        # Функция доступна когда сформирована коллегия
        return case_services.case_get_all_qs().filter(
            secretary=self.request.user,
            paused=False,
            stopped=False,
            stage_step__code=4000,
        ).exclude(document__sign__timestamp='')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        return reverse_lazy('cases-detail', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Типы документов, которые будут сгенерированы
        context['docs_to_generate'] = classifiers_services.get_doc_types_for_meeting_holding(
            self.object.claim.claim_kind_id
        )

        return context


@method_decorator(group_required('Секретар'), name='dispatch')
class DocumentAddView(LoginRequiredMixin, CreateView):
    """Страница создания вторичного документа."""
    model = Document
    template_name = 'cases/document_add/index.html'
    form_class = DocumentAddForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = case_services.case_get_all_qs().filter(
            secretary=self.request.user,
            stopped=False,
            pk=self.kwargs['pk']
        ).first()
        if not context['case']:
            raise Http404

        return context

    def form_valid(self, form):
        form.instance.case_id = self.kwargs['pk']
        res = super().form_valid(form)
        document_services.document_add_history(form.instance.pk, 'Документ додано у систему', self.request.user.pk)
        case_services.case_add_history_action(
            form.instance.case_id,
            f'Додано документ до справи (тип документа: {form.instance.document_type.title})',
            self.request.user.pk
        )
        return res

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Документ успішно додано до справи.')
        return reverse_lazy('cases-detail', kwargs={'pk': self.kwargs['pk']})


@method_decorator(group_required('Секретар'), name='dispatch')
class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    """Страница обновления файла документа."""
    model = Document
    template_name = 'cases/document_update/index.html'
    form_class = DocumentUpdateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = self.object.case
        if not context['case'].secretary == self.request.user:
            raise Http404

        return context

    def form_valid(self, form):
        res = super().form_valid(form)
        # Запись в историю дела и документа
        message = 'Оновлено файл документу'
        document_services.document_add_history(form.instance.pk, message, self.request.user.pk)
        case_services.case_add_history_action(form.instance.case_id, message, self.request.user.pk)
        return res

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Документ успішно оновлено.')
        return reverse_lazy('cases-detail', kwargs={'pk': self.object.case.pk})


@group_required('Секретар')
def document_delete(request, pk: int):
    """Удаление документа."""
    document = document_services.document_soft_delete(pk, request.user)
    if document:
        case_services.case_add_history_action(
            document.case_id,
            f'Видалено документ "{document.document_type.title}"',
            request.user.pk
        )
        messages.add_message(request, messages.SUCCESS, 'Документ успішно видалено.')
        return redirect('cases-detail', pk=document.case_id)
    raise Http404


@group_required('Секретар')
def document_send_to_sign(request, pk: int):
    # Получение документа
    document = document_services.document_get_by_id(pk)

    # Проверка, не созданы ли записи для подписи
    if document.sign_set.count():
        raise Http404

    # Проверка является ли пользователь секретарём дела
    if document.case.secretary_id != request.user.id:
        raise Http404

    # Создание записей для подписи
    document_services.document_create_sign_records(document.pk)

    # Проверка какому стадии соответствует дело, смена стадии, выполнение сопутствующих стадии операций
    stage_set_service = case_stage_step_change_action_service.CaseSetActualStageStepService(
        case_stage_step_change_action_service.CaseStageStepQualifier(),
        document.case,
        request,
        NotificationService([DbChannel()])
    )
    stage_set_service.execute()

    # Переадресация на страницу дела
    return redirect('cases-detail', pk=document.case.pk)


@group_required('Секретар')
def document_send_to_chancellary(request, pk: int):
    """Отправляет документ в АС Вихідні документи"""
    document = document_services.document_get_by_id(pk)
    if not document.sent_to_chancellary:
        document_services.document_send_to_chancellary(pk, request.user.pk)
        messages.add_message(request, messages.SUCCESS, 'Документ успішно відправлено до АС "Вихідні документи"')
        return redirect('cases-detail', pk=document.case.pk)
    raise Http404('Документ вже був відправлений до АС "Вихідні документи"')


@login_required
def cases_get_current_cases(request, user_id: int):
    """Возвращает HTML для модального окна с инф-ей о текущих ап. делах пользователя."""
    cases = case_services.case_get_user_cases_current(user_id)
    return render(request, 'cases/user_current_cases.html', {'cases': cases})


@login_required
def cases_get_finished_cases(request, user_id: int):
    """Возвращает HTML для модального окна с инф-ей о законченных ап. делах пользователя."""
    cases = case_services.case_get_user_cases_finished(user_id)
    return render(request, 'cases/user_finished_cases.html', {'cases': cases})


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

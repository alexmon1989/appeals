import json

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets

from ..users import services as users_services
from ..common.utils import files_to_base64

from .services import services
from ..filling import services as filling_services
from .models import Case
from .permissions import HasAccessToCase
from .serializers import DocumentSerializer, CaseSerializer
from ..common.mixins import LoginRequiredMixin
from .tasks import upload_sign_task
from ..classifiers import services as classifiers_services


@login_required
def cases_list(request):
    """Отображает страницу со списком апелляционных дел."""
    obj_kinds = classifiers_services.get_obj_kinds_list()
    return render(request, 'cases/list/index.html', {'obj_kinds': obj_kinds})


class CasesViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает JSON с документами дела."""
    serializer_class = CaseSerializer

    def get_queryset(self):
        all_cases = services.case_get_list()
        return services.case_filter_dt_list(
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
        return services.case_get_list()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stages'] = services.case_get_stages(self.object.pk)
        context['claim'] = filling_services.claim_get_data_by_id(self.object.claim.pk)
        return context


class CaseCreateView(LoginRequiredMixin, CreateView):
    """Отображает страницу создания апелляционного дела."""
    model = Case
    template_name = 'cases/create/index.html'
    fields = ['case_number']


@require_POST
@login_required
def upload_sign(request, document_id: int):
    """Загружает на сервер информацию о цифровой подписи документа."""
    files_base64 = files_to_base64(request.FILES)

    task = upload_sign_task.delay(
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


class DocumentsViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает JSON с документами дела."""
    serializer_class = DocumentSerializer
    permission_classes = (HasAccessToCase,)

    def get_queryset(self):
        return services.case_get_documents_list(self.kwargs['id'])


def document_signs_info(request, document_id: int):
    """Отображает информацию о цифровых подписях документа."""
    document = services.document_get_by_id(document_id)
    return render(request, 'cases/detail/document_signs_info.html', {'document': document})


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

import json

from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from urllib.parse import unquote
from pathlib import Path
from rest_framework import viewsets

from .services import services
from .models import Case
from .permissions import HasAccessToCase
from .serializers import DocumentSerializer
from ..common.mixins import LoginRequiredMixin


@login_required
def cases_list(request):
    """Отображает страницу со списком апелляционных дел."""
    cases = services.case_get_list(user=request.user)
    return render(request, 'cases/list/index.html', {'cases': cases})


class CaseDetailView(LoginRequiredMixin, DetailView):
    """Отображает страницу апелляционного дела."""
    model = Case
    template_name = 'cases/detail/index.html'

    def get_queryset(self):
        return services.case_get_list(user=self.request.user)


class CaseCreateView(LoginRequiredMixin, CreateView):
    """Отображает страницу создания апелляционного дела."""
    model = Case
    template_name = 'cases/create/index.html'
    fields = ['case_number']


@require_POST
@login_required
def upload_sign(request, document_id: int):
    """Загружает на сервер информацию о цифровой подписи документа."""
    # Получение документа
    document = services.document_get_by_id(document_id)
    if document and services.document_can_be_signed_by_user(document, request.user):
        # Загрузка файла
        relative_path = Path(unquote(f"{document.file}_{request.user.pk}.p7s"))
        sign_destination = Path(settings.MEDIA_ROOT) / relative_path
        if services.sign_upload(request.FILES['blob'], sign_destination):
            # Создание объекта цифровой подписи в БД
            sign_info = json.loads(request.POST['sign_info'])
            sign_data = {
                'document': document,
                'file': str(relative_path),
                'user': request.user,
                'subject': sign_info['subject'],
                'serial_number': sign_info['serial'],
                'issuer': sign_info['issuer'],
                'timestamp': sign_info['timestamp'],
            }
            services.sign_create(sign_data)

            services.document_add_sign_info_to_file(document_id)

        return JsonResponse({'success': 1})

    return JsonResponse({'success': 0})


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

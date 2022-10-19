from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.views.generic.edit import CreateView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import permissions

from . import services
from .models import Absence
from .forms import AbsenceForm
from apps.common.mixins import LoginRequiredMixin


@login_required
def index(request):
    """Отображает основную страницу приложения."""
    context = {
        'invitations': services.invitation_get_list_qs(request.user.id),
        'absences': services.absence_get_all_qs(request.user.id),
    }
    return render(request, 'meetings/index/index.html', context)


class AbsenceCreateView(LoginRequiredMixin, CreateView):
    """Страница создания периода отсутствия пользователя."""
    model = Absence
    template_name = 'meetings/absence_create/index.html'
    success_url = reverse_lazy('meetings-index')
    form_class = AbsenceForm
    success_message = 'Період відсутності успішно додано'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.get_success_url())


@login_required
def invitation_accept(request, pk):
    """Принятие предложения об участии в заседании."""
    if services.invitation_accept(pk, request.user.pk):
        messages.success(request, "Запит на участь у засідання прийнято. "
                                  "Подія з'явиться у календарі коли усі інші запрошені особи приймуть запрошення.")
        # todo Оповещение секретарю дела

        return redirect('meetings-index')
    raise Http404


@login_required
def invitation_reject(request, pk):
    """Отказ от предложения об участии в заседании."""
    if services.invitation_reject(pk, request.user.pk):
        messages.info(request, 'Запит на участь у засідання відхилено.')
        # todo Оповещение секретарю дела

        return redirect('meetings-index')
    raise Http404


@login_required
def delete_absence(request, pk):
    """Удаляет период отсутствия пользователя."""
    deleted_num, deleted_obj_types = services.absense_delete_one(pk, request.user.pk)
    if deleted_num:
        messages.success(request, 'Період відсутності успішно видалено.')
        return redirect('meetings-index')
    raise Http404


class ListEventsAPIView(APIView):
    """Отображает список события для календаря"""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """Возвращает список событий для календаря."""
        try:
            start = request.GET['start'][:10]
            end = request.GET['end'][:10]
        except KeyError:
            raise Http404

        meetings = services.meeting_get_calendar_events(request.user.pk, start, end)
        absences = services.absence_get_calendar_events(request.user.pk, start, end)
        return Response(meetings + absences)


class EventDetailAPIView(APIView):
    """Отображает список события для календаря"""
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            obj_id = request.GET['id']
        except KeyError:
            raise Http404
        if 'meeting_' in obj_id:
            obj_id = int(obj_id.replace('meeting_', ''))
            return Response(
                {
                    'meeting': services.meeting_get_one(obj_id, request.user.pk)
                },
                template_name='meetings/index/_partials/meeting_detail.html'
            )
        elif 'absence_' in obj_id:
            obj_id = int(obj_id.replace('absence_', ''))
            return Response(
                {
                    'absense': services.absense_get_one(obj_id, request.user.id)
                },
                template_name='meetings/index/_partials/absenсe_detail.html'
            )
        else:
            raise Http404

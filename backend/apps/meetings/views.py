from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import permissions

from . import services
from .models import Absence, Meeting
from .forms import AbsenceForm, MeetingForm
from apps.common.mixins import LoginRequiredMixin
from apps.cases.services import case_stage_step_change_action_service, case_services
from apps.notifications.services import Service as NotificationService, DbChannel


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
        # Оповещение секретарю дела
        case = services.invitation_get_one(pk).meeting.case
        secretary_id = case.secretary_id
        case_number = case.case_number
        notification_service = NotificationService([DbChannel()])
        notification_service.execute(
            f"{request.user.get_full_name} прийняв(ла) запрошення до участі у засіданні АП "
            f"щодо справи № <a href=\"{reverse('cases-detail', kwargs={'pk': case.pk})}\">{case_number}</a>.",
            [secretary_id]
        )

        # Изменение стадии дела, создание оповещений
        stage_set_service = case_stage_step_change_action_service.CaseSetActualStageStepService(
            case_stage_step_change_action_service.CaseStageStepQualifier(),
            case,
            request,
            NotificationService([DbChannel()])
        )
        stage_set_service.execute()

        return redirect('meetings-index')
    raise Http404


@login_required
def invitation_reject(request, pk):
    """Отказ от предложения об участии в заседании."""
    if services.invitation_reject(pk, request.user.pk):
        messages.info(request, 'Запит на участь у засідання відхилено.')
        # Оповещение секретарю дела
        case = services.invitation_get_one(pk).meeting.case
        secretary_id = case.secretary_id
        case_number = case.case_number
        notification_service = NotificationService([DbChannel()])
        notification_service.execute(
            f"{request.user.get_full_name} відхилив(ла) запрошення до участі у засіданні АП "
            f"щодо справи № <a href=\"{reverse('cases-detail', kwargs={'pk': case.pk})}\">{case_number}</a>.",
            [secretary_id]
        )

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


class MeetingCreateView(LoginRequiredMixin, CreateView):
    """Страница создания апеляционного заседания."""
    model = Meeting
    template_name = 'meetings/create/index.html'
    success_url = reverse_lazy('meetings-index')
    form_class = MeetingForm
    success_message = 'Апеляційне засідання успішно створене.'
    case = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['case'] = self.case = case_services.case_get_one(self.kwargs['case_id'])
        if not self.case:
            raise Http404
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['case'] = self.case
        context['absences'] = services.absence_get_users_periods(
            [item.person_id for item in self.case.collegiummembership_set.all()]
        )
        return context

    def get_success_url(self):
        return reverse('cases-detail', kwargs={'pk': self.kwargs['case_id']})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.case_id = self.kwargs['case_id']
        self.object.save()
        messages.success(self.request, self.success_message)

        # Создание приглашений
        services.invitation_create_collegium_invitations(self.object.pk)

        # Изменение стадии дела, создание оповещений
        stage_set_service = case_stage_step_change_action_service.CaseSetActualStageStepService(
            case_stage_step_change_action_service.CaseStageStepQualifier(),
            self.object.case,
            self.request,
            NotificationService([DbChannel()])
        )
        stage_set_service.execute()

        return HttpResponseRedirect(self.get_success_url())


class MeetingDetailView(DetailView):
    """Возвращает html с информацией о заседании."""
    model = Meeting
    template_name = 'meetings/detail.html'

    def get_queryset(self):
        return Meeting.objects.prefetch_related('invitation_set', 'invitation_set__user')


@login_required
def get_user_absence_info(request, user_id: int):
    """Возвращает HTML для модального окна с инф-ей об периодах отсутствия пользователя."""
    absences = services.absence_get_all_qs(user_id).order_by('-date_from')[:10]
    return render(request, 'meetings/user_absence_info.html', {'absences': absences})

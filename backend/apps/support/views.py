from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
from django.utils import timezone
from django.http import Http404

from .models import Ticket
from .forms import CreateTicketForm, CloseTicketForm
from apps.common.mixins import LoginRequiredMixin, StaffRequiredMixin
from apps.notifications.services import Service as NotificationService, DbChannel
from apps.users import services as user_services


class TicketListView(LoginRequiredMixin, ListView):
    """Отображает страницу с заявками"""
    model = Ticket
    template_name = 'support/list/index.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        """Возвращает QS."""
        if self.request.user.is_staff:
            # Если пользователь - админ, то необходимо показывать все заявки
            return Ticket.objects.order_by('-created_at')
        else:
            # Для обычного пользователя необходимо показывать только его заявки
            return Ticket.objects.filter(send_by=self.request.user).order_by('-created_at')


class TicketCreateView(LoginRequiredMixin, CreateView):
    """Отображает страницу создания заявки."""
    template_name = 'support/create/index.html'
    model = Ticket
    form_class = CreateTicketForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Заявку успішно створено.')
        return reverse('support-index')


class TicketDetailView(LoginRequiredMixin, DetailView):
    """Отображает страницу с детальной информацией о заявке."""
    template_name = 'support/detail/index.html'
    model = Ticket

    def get_queryset(self):
        if self.request.user.is_staff:
            # Если пользователь - админ, то необходимо показывать все заявки
            return Ticket.objects.all()
        else:
            # Для обычного пользователя необходимо показывать только его заявки
            return Ticket.objects.filter(send_by=self.request.user)


def delete_ticket(request, pk: int):
    """Удаление заявки."""
    # Пользователь может удалить только свою, не принятую в работу, заявку
    ticket = Ticket.objects.filter(pk=pk, send_by=request.user, status=1).first()
    if ticket:
        ticket.delete()
    messages.add_message(request, messages.SUCCESS, 'Заявку успішно видалено.')
    return redirect('support-index')


def take_to_work(request, pk: int):
    """Принимает заявку в работу."""
    if not request.user.is_staff:
        raise Http404
    ticket = Ticket.objects.filter(pk=pk, status=1).first()
    if ticket:
        ticket.taken_to_work_by = request.user
        ticket.taken = timezone.now()
        ticket.status = 2
        ticket.save()

        message = f'Заявку №{ticket.pk} прийнято у роботу.'
        messages.add_message(request, messages.SUCCESS, message)

        # Оповещение пользователю
        ticket_url = reverse('support-detail-ticket', kwargs={'pk': ticket.pk})
        message = f"Заявку в технічну підтримку <a href='{ticket_url}'>№{ticket.pk}</a> прийнято до роботи."
        notification_service = NotificationService([DbChannel()])
        users = [ticket.send_by.pk]
        notification_service.execute(
            message,
            users
        )

        return redirect('support-detail-ticket', pk=ticket.pk)

    raise Http404


class TicketCloseView(StaffRequiredMixin, UpdateView):
    """Отображает страницу закрытия заявки."""
    template_name = 'support/close/index.html'
    model = Ticket
    form_class = CloseTicketForm

    def get_queryset(self):
        return Ticket.objects.filter(status=2)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, 'Заявку успішно закрито.')
        return reverse('support-index')

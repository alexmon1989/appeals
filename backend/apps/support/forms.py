from django import forms
from django.utils import timezone
from django.shortcuts import reverse

from .models import Ticket
from apps.notifications.services import Service as NotificationService, DbChannel
from apps.users import services as user_services

from crispy_forms.helper import FormHelper


class CreateTicketForm(forms.ModelForm):
    """Форма создания заявки в тех. поддержку."""

    class Meta:
        model = Ticket
        fields = ('text', 'file_1', 'file_2', 'file_3')

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.label_class = "fw-bold"
        self.helper.form_tag = False

    def save(self, commit=True):
        self.instance.send_by = self.request.user
        self.instance.save()

        # Оповещение администраторов
        ticket_url = reverse('support-detail-ticket', kwargs={'pk': self.instance.pk})
        message = f"Створено заявку <a href='{ticket_url}'>№{self.instance.pk}</a> у технічну підтримку."
        notification_service = NotificationService([DbChannel()])
        users = [user.pk for user in user_services.user_get_staff()]
        notification_service.execute(
            message,
            users
        )


class CloseTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = 'comment',

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.label_class = "fw-bold"
        self.helper.form_tag = False

    def save(self, commit=True):
        self.instance.closed_by = self.request.user
        self.instance.closed = timezone.now()
        self.instance.status = 3
        self.instance.save()

        # Оповещение пользователя
        ticket_url = reverse('support-detail-ticket', kwargs={'pk': self.instance.pk})
        message = f"Заявку в технічну підтримку <a href='{ticket_url}'>№{self.instance.pk}</a> закрито."
        notification_service = NotificationService([DbChannel()])
        users = [self.instance.send_by.pk]
        notification_service.execute(
            message,
            users
        )

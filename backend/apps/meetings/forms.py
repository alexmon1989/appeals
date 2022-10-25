from django import forms
from django.contrib.auth import get_user_model
from django.forms.widgets import DateInput, DateTimeInput
from django.utils import timezone

from crispy_forms.helper import FormHelper

from .models import Absence, Invitation, Meeting
from . import services


UserModel = get_user_model()


class UserField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name_initials()


class AbsenceAdminForm(forms.ModelForm):
    user = UserField(
        queryset=UserModel.objects.exclude(last_name__isnull=True).order_by('last_name', 'first_name', 'middle_name'),
        label='Співробітник'
    )

    class Meta:
        model = Absence
        fields = '__all__'


class AbsenceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.form_id = "absence-create-form"
        self.helper.label_class = "fw-bold"
        self.helper.field_class = "mb-4"

    class Meta:
        model = Absence
        fields = ['date_from', 'date_to']
        widgets = {
            'date_from': DateInput(attrs={'type': 'date'}),
            'date_to': DateInput(attrs={'type': 'date'})
        }

    def clean_date_from(self):
        data = self.cleaned_data['date_from']
        if data < timezone.now().date():
            raise forms.ValidationError("Значення поля має містити сьогоднішню або майбутню дату.")
        return data

    def clean_date_to(self):
        data = self.cleaned_data['date_to']
        if data < timezone.now().date():
            raise forms.ValidationError('Значення поля має містити сьогоднішню або майбутню дату.')
        if data < self.cleaned_data['date_from']:
            raise forms.ValidationError('Значення поля має містити дату, що більше або рівна даті у полі "Дата з".')
        return data


class InvitationAdminForm(AbsenceAdminForm):
    class Meta:
        model = Invitation
        fields = '__all__'


class MeetingForm(forms.ModelForm):
    """Форма создания заседания."""

    def __init__(self, case, *args, **kwargs):
        self.case = case
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.form_id = "meeting-create-form"
        self.helper.label_class = "fw-bold"
        self.helper.field_class = "mb-4"

    class Meta:
        model = Meeting
        fields = ['datetime']
        widgets = {
            'datetime': DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_datetime(self):
        """Валидация поля времени апеляцинного заседания."""
        data = self.cleaned_data['datetime']
        if data < timezone.now():
            raise forms.ValidationError("Значення поля має містити сьогоднішню або майбутню дату.")

        # Валидация отсутствий членов коллегии
        if not services.absence_users_present_on_date(
            data,
            [item.person_id for item in self.case.collegiummembership_set.all()]
        ):
            raise forms.ValidationError("Один або більше членів колегії відсутні на дату, вказану у полі.")

        return data
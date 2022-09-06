from django import forms
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div

from dateutil.relativedelta import relativedelta

from .models import Case
from ..classifiers.models import RefusalReason
from .services import case_services

import random


UserModel = get_user_model()


class UserField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name


class UserFieldMultiple(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name


class CaseUpdateForm(forms.ModelForm):
    goto_2001 = forms.BooleanField(
        required=False,
        label=mark_safe('Перейти до стадії <b>"Досьє заповнено. Очікує на розподіл колегії" (код стадії - 2001)</b>.')
    )
    expert = UserField(
        queryset=UserModel.objects.filter(groups__name='Секретар').order_by('last_name', 'first_name', 'middle_name'),
        label='Експерт',
        required=False
    )
    submission_date = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date', 'readonly': True}
        ),
        label='Дата подання звернення'
    )
    deadline = forms.DateField(
        widget=forms.TextInput(
            attrs={'type': 'date', 'readonly': True}
        ),
        label='Дата, до якої необхідно розглянути звернення'
    )

    class Meta:
        model = Case
        fields = ['refusal_reasons', 'expert', 'deadline']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        if self.instance.claim.claim_kind.claim_sense == 'DE':
            self.fields['refusal_reasons'] = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                queryset=RefusalReason.objects.filter(obj_kind=self.instance.claim.obj_kind),
                label='Підстава, з якої оскаржується рішення за запереченням'
            )
        elif self.instance.claim.claim_kind.claim_sense == 'AP':
            self.fields['refusal_reasons'] = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                queryset=RefusalReason.objects.filter(obj_kind=self.instance.claim.obj_kind),
                label='Підстава, з якої визнається недійсним охоронний документ за апеляційною заявою',
            )
        else:
            del self.fields['refusal_reasons']

        self.fields['submission_date'].initial = self.instance.claim.submission_date.strftime('%Y-%m-%d')
        self.fields['submission_date'].help_text = 'Недоступне для редагування, оскільки канал надходження звернення - "веб-форма"'
        if not self.initial['deadline']:
            self.initial['deadline'] = (self.instance.claim.submission_date + relativedelta(months=2)).strftime('%Y-%m-%d')
        self.fields['deadline'].help_text = 'Значення формується автоматично'

        self.helper = FormHelper()
        self.helper.form_id = "case-update-form"
        self.helper.label_class = "fw-bold"
        self.helper.field_class = "mb-4"

        fields = []
        if 'refusal_reasons' in self.fields:
            fields.append('refusal_reasons')
        fields.append('expert')
        fields.append('submission_date')
        fields.append('deadline')
        if self.instance.stage_step.code == 2000:
            fields.append('goto_2001')
        fields.append(Div(template='cases/update/_partials/submit.html'))

        self.helper.layout = Layout(*fields)

    def save(self, commit=True):
        super().save()
        case_services.case_add_history_action(self.instance.id, 'Зміна даних справи', self.user.pk)

        # Переход к стадии 2001 - "Досьє заповнено. Очікує на розподіл колегії."
        if self.cleaned_data.get('goto_2001') and self.instance.stage_step.code == 2000:
            case_services.case_change_stage_step(self.instance.pk, 2001, self.user.pk)


class CaseCreateCollegiumForm(forms.ModelForm):
    """Форма создания коллегии."""
    # Подписант (варианты выбора - глава коллегии (глава АП + заместители))
    signer = UserField(
        queryset=UserModel.objects.filter(
            groups__name__in=['Голова Апеляційної палати', 'Заступник голови Апеляційної палати']
        ).order_by('last_name', 'first_name', 'middle_name').distinct(),
        label='Підписант документу розпорядження про створення колегії',
        required=True
    )

    class Meta:
        model = Case
        fields = []

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        # Глава коллегии (варианты выбора в зависимости от специальности (типа объекта ИС обращения)).
        # Если обращенеие - "Заява про визнання торговельної марки добре відомою в Україні",
        # то голова коллегии всегда голова АП
        if self.instance.claim.claim_kind.pk == 12:
            head_choices = UserModel.objects.filter(
                groups__name='Голова Апеляційної палати'
            ).order_by('last_name', 'first_name', 'middle_name')
        else:
            head_choices = UserModel.objects.filter(
                specialities=self.instance.claim.obj_kind
            ).order_by('last_name', 'first_name', 'middle_name')
        head_initial = head_choices[random.randint(0, head_choices.count()-1)]
        self.fields['head'] = UserField(
            queryset=head_choices,
            label='Голова колегії',
            initial=head_initial
        )

        # Члены коллегии (варианты выбора в зависимости от специальности (типа объекта ИС обращения))
        members_choices = UserModel.objects.filter(
            specialities=self.instance.claim.obj_kind
        ).order_by('last_name', 'first_name', 'middle_name')
        members_initial = []
        while True:
            random_member = members_choices[random.randint(0, members_choices.count()-1)]
            if random_member != head_initial and random_member not in members_initial:
                members_initial.append(random_member)
            if len(members_initial) == 2:
                break
        self.fields['members'] = UserFieldMultiple(
            widget=forms.CheckboxSelectMultiple,
            queryset=members_choices,
            label='Члени колегії',
            initial=members_initial,
        )

        self.helper = FormHelper()
        self.helper.form_id = "case-create-collegium-form"
        self.helper.label_class = "fw-bold"
        self.helper.field_class = "mb-4"

        fields = []
        fields.append('head')
        fields.append('members')
        fields.append('signer')

        self.helper.layout = Layout(*fields)

    def clean_members(self):
        """Валадация поля членов коллегии."""
        data = self.cleaned_data['members']
        if len(data) != 2:
            raise ValidationError("Будь ласка, оберіть двох членів колегії.")
        return data

    def save(self, commit=True):
        # Создание коллегии
        data = {
          'case_id': self.instance.pk,
          'head_id': self.cleaned_data['head'].pk,
          'members_ids': [x.pk for x in self.cleaned_data['members']],
          'signer_id': self.cleaned_data['signer'].pk,
          'user_id': self.user.pk,
        }
        case_services.case_create_collegium(**data)

from django import forms
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.utils import timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div
from django_select2 import forms as s2forms

from dateutil.relativedelta import relativedelta

from .models import Case, Document
from apps.classifiers.models import RefusalReason, DecisionType
from .services import case_services, case_stage_step_change_action_service
from apps.notifications.services import Service as NotificationService, DbChannel
from apps.meetings import services as meetings_services

import random


UserModel = get_user_model()


class UserField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name


class UserFieldMultiple(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name


class CaseUpdateForm(forms.ModelForm):
    """Форма редактирования данных дела."""
    goto_2001 = forms.BooleanField(
        required=False,
        label=mark_safe('Перейти до стадії <b>"Досьє заповнено. Очікує на розподіл колегії" (код стадії - 2001)</b>.')
    )
    expert = UserField(
        queryset=UserModel.objects.filter(groups__name='Експерт').order_by('last_name', 'first_name', 'middle_name'),
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

    def __init__(self, request, *args, **kwargs):
        self.request = request
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
        case_services.case_add_history_action(self.instance.id, 'Зміна даних справи', self.request.user.pk)
        messages.success(self.request, 'Дані успішно збережено.')

        # Переход к стадии 2001 - "Досьє заповнено. Очікує на розподіл колегії."
        if self.cleaned_data.get('goto_2001') and self.instance.stage_step.code == 2000:
            stage_set_service = case_stage_step_change_action_service.CaseSetActualStageStepService(
                case_stage_step_change_action_service.CaseStageStepQualifier(),
                self.instance,
                self.request,
                NotificationService([DbChannel()])
            )
            stage_set_service.execute()


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

    def __init__(self, request, *args, **kwargs):
        self.request = request
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

        fields = ['head', 'members', 'signer']

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
          'user_id': self.request.user.pk,
        }
        case_services.case_create_collegium(**data)
        self.instance.refresh_from_db()

        # Изменение стадии дела, создание оповещений
        stage_set_service = case_stage_step_change_action_service.CaseSetActualStageStepService(
            case_stage_step_change_action_service.CaseStageStepQualifier(),
            self.instance,
            self.request,
            NotificationService([DbChannel()])
        )
        stage_set_service.execute()


class CaseAcceptForConsiderationForm(forms.ModelForm):
    """Форма принятия дела к рассмотрению."""

    class Meta:
        model = Case
        fields = []

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        if self.instance.claim.claim_kind.claim_sense == 'AP':
            # Если апеляционное заявление, то необходимо создать предварительное заседание,
            # поэтому на форме должно быть поле выбора даты этого заседания
            self.fields['pre_meeting_datetime'] = forms.DateTimeField(
                widget=forms.DateTimeInput(
                    attrs={'type': 'datetime-local'}
                ),
                label='Дата та час підготовчого засідання'
            )

        self.helper = FormHelper()
        self.helper.form_id = "case-consider-for-acceptance-form"
        self.helper.label_class = "fw-bold"
        self.helper.field_class = "mb-4"

    def clean_pre_meeting_datetime(self):
        data = self.cleaned_data['pre_meeting_datetime']
        if data < timezone.now():
            raise forms.ValidationError("Значення поля має містити сьогоднішню або майбутню дату.")
        return data

    def save(self, commit=True):
        # Создание предварительного заседания в случае апел. заявления
        if self.instance.claim.claim_kind.claim_sense == 'AP':
            meetings_services.meeting_create_pre_meeting(
                self.cleaned_data['pre_meeting_datetime'],
                self.instance.pk
            )

        # Создание документов
        data = {
            'case_id': self.instance.pk,
            'user_id': self.request.user.pk,
            'signer_id': self.instance.collegium_head.pk,
        }
        case_services.case_create_docs_consider_for_acceptance(**data)
        self.instance.refresh_from_db()

        # Изменение стадии дела, создание оповещений
        stage_set_service = case_stage_step_change_action_service.CaseSetActualStageStepService(
            case_stage_step_change_action_service.CaseStageStepQualifier(),
            self.instance,
            self.request,
            NotificationService([DbChannel()])
        )
        stage_set_service.execute()


class CasePausingForm(forms.ModelForm):
    """Форма остановки рассмотрения дела."""
    # Тип документа
    document_type = forms.ChoiceField(
        label='Тип документа, який буде сгенеровано',
        help_text='Підписант документа - голова колегії'
    )
    circumstances = forms.CharField(
        label='Обставини / виявлені недоліки',
        required=False,
        help_text='Значення поля буде додано у згенерований файл .docx'
    )
    reason = forms.CharField(
        label='Підстави',
        required=False,
        help_text='Значення поля буде додано у згенерований файл .docx'
    )

    class Meta:
        model = Case
        fields = ['document_type']

    def __init__(self, request, doc_types, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        self.fields['document_type'].choices = ((x['code'], x['title']) for x in doc_types)

        self.helper = FormHelper()
        self.helper.form_id = "case-pausing-form"
        self.helper.label_class = "fw-bold"
        self.helper.field_class = "mb-4"

    def save(self, commit=True):
        # Генерация документов
        case_services.case_create_docs(
            case_id=self.instance.pk,
            doc_types_codes=[self.cleaned_data['document_type']],
            user_id=self.request.user.pk,
            signer_id=self.instance.collegium_head.pk,  # Подписант - глава коллегии
            form_data=self.cleaned_data,
        )

        # Остановка дела
        self.instance.paused = True
        self.instance.save()

        # Запись в историю дела
        case_services.case_add_history_action(
            self.instance.id,
            'Залишення без розгляду / зупинка розгляду',
            self.request.user.pk
        )


class CaseStoppingForm(forms.ModelForm):
    """Форма признания дела непригодным к рассмотрению."""
    # Тип документа
    document_type = forms.ChoiceField(
        label='Тип документа, який буде сгенеровано',
        help_text='Підписант документа - голова колегії'
    )
    reason = forms.CharField(
        label='Підстави',
        required=False,
        help_text='Значення поля буде додано у згенерований файл .docx'
    )
    circumstances = forms.CharField(
        label='Обставини',
        required=False,
        help_text='Значення поля буде додано у згенерований файл .docx'
    )

    class Meta:
        model = Case
        fields = ['document_type']

    def __init__(self, request, doc_types, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        self.fields['document_type'].choices = ((x['code'], x['title']) for x in doc_types)

        self.helper = FormHelper()
        self.helper.form_id = "case-stopping-form"
        self.helper.label_class = "fw-bold"
        self.helper.field_class = "mb-4"

    def save(self, commit=True):
        # Генерация документов
        case_services.case_create_docs(
            case_id=self.instance.pk,
            doc_types_codes=[self.cleaned_data['document_type']],
            user_id=self.request.user.pk,
            signer_id=self.instance.collegium_head.pk,  # Подписант - глава коллегии
            form_data=self.cleaned_data,
        )

        # Остановка дела
        self.instance.stopped = True
        self.instance.save()

        # Запись в историю дела
        case_services.case_add_history_action(
            self.instance.id,
             'Вважати неподаним / не підлягає розгляду',
            self.request.user.pk
        )


class DocumentTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "title__icontains",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.i18n_name = 'uk'


class DocumentAddForm(forms.ModelForm):
    """Форма загрузки вторичных документов."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.form_id = "document-add-form"
        self.helper.label_class = "fw-bold"
        self.helper.field_class = "mb-4"

    class Meta:
        model = Document
        fields = ['document_type', 'file']
        widgets = {
            "document_type": DocumentTypeWidget(
                attrs={
                    'data-minimum-input-length': 0,
                    'data-allow-clear': True,
                    'data-placeholder': 'Оберіть тип документа',
                    'data-theme': 'bootstrap-5',
                    'data-container-css-class': '',
                    'data-dropdown-css-class': 'select2--small',
                }
            ),
        }


class DocumentUpdateForm(forms.ModelForm):
    """Форма обновления документа."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.form_id = "document-update-form"
        self.helper.label_class = "fw-bold"
        self.helper.field_class = "mb-4"

    class Meta:
        model = Document
        fields = ['file']


class CaseMeetingForm(forms.ModelForm):
    """Форма проведения ап. заседания."""
    # Заседания
    meeting = forms.ChoiceField(
        label='Засідання',
    )
    # Возможные решения АП
    decision = forms.ModelChoiceField(
        label='Рішення',
        queryset=DecisionType.objects.all()
    )

    class Meta:
        model = Case
        fields = ['meeting', 'decision']

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        self.fields['meeting'].choices = (
            (x.pk, x.datetime) for x in self.instance.meeting_set.filter(
                meeting_type='COMMON',
                datetime__gte=timezone.now()
            )
        )
        self.fields['decision'].queryset = DecisionType.objects.filter(claim_kinds=self.instance.claim.claim_kind_id)

        self.helper = FormHelper()
        self.helper.form_id = "case-meeting-form"
        self.helper.label_class = "fw-bold"
        self.helper.field_class = "mb-4"

    def save(self, commit=True):
        # Сохранение решения совещания
        self.instance.decision_type = self.cleaned_data['decision']
        self.instance.save()

        # Запись в историю дела
        case_services.case_add_history_action(
            self.instance.id,
            f'Встановлено рішення апеляційної палати: {self.instance.decision_type.title}',
            self.request.user.pk
        )

        # Создание документов
        case_services.case_create_docs_for_meeting_holding(self.instance.pk, self.request.user.pk)
        self.instance.refresh_from_db()

        # Изменение стадии дела, создание оповещений
        stage_set_service = case_stage_step_change_action_service.CaseSetActualStageStepService(
            case_stage_step_change_action_service.CaseStageStepQualifier(),
            self.instance,
            self.request,
            NotificationService([DbChannel()])
        )
        stage_set_service.execute()

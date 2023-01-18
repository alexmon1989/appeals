from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

from apps.classifiers.models import ClaimKind, DecisionType, RefusalReason

PERSON_TYPES = (
    ('', 'Оберіть тип особи...'),
    ('appellant', 'Апелянт'),
    ('represent', 'Представник апелянта'),
    ('collegium_head', 'Голова колегії'),
    ('collegium_member', 'Член колегії'),
    ('expert', 'Експерт'),
)

HAS_DECISION = (
    ('', 'Оберіть значення...'),
    ('no', 'Рішення відсутнє'),
    ('yes', 'Є рішення АП'),
)


class SearchForm(forms.Form):
    """Форма пошуку."""
    person_type = forms.ChoiceField(
        choices=PERSON_TYPES,
        label='Тип особи',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select-sm'})
    )
    person_name = forms.CharField(
        label='ПІБ особи',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Іванов Іван Іванович', 'class': 'form-control-sm'})
    )
    case_number = forms.CharField(
        label='Номер справи',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'ТМ-З-202212-007', 'class': 'form-control-sm'})
    )
    case_date_from = forms.DateField(
        label='Дата подачі звернення (від)',
        required=False,
        widget=forms.DateInput(
            attrs={'placeholder': 'Дата подачі звернення (від)', 'class': 'form-control-sm', 'type': 'date'}
        )
    )
    case_date_to = forms.DateField(
        label='Дата подачі звернення (до)',
        required=False,
        widget=forms.DateInput(
            attrs={'placeholder': 'Дата подачі звернення (до)', 'class': 'form-control-sm', 'type': 'date'}
        )
    )
    obj_number = forms.CharField(
        label='Номер ОПІВ',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'm202204122', 'class': 'form-control-sm'})
    )
    obj_title = forms.CharField(
        label='Назва ОПІВ',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Tesla', 'class': 'form-control-sm'})
    )
    claim_kind = forms.ChoiceField(
        label='Вид звернення',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select-sm'})
    )
    refusal_reason = forms.ChoiceField(
        label='Підстава для оскарження',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select-sm'})
    )
    meeting_date_from = forms.DateField(
        label='Дата засідання (від)',
        required=False,
        widget=forms.DateInput(
            attrs={'placeholder': 'Дата подачі звернення (до)', 'class': 'form-control-sm', 'type': 'date'}
        )
    )
    meeting_date_to = forms.DateField(
        label='Дата засідання (до)',
        required=False,
        widget=forms.DateInput(
            attrs={'placeholder': 'Дата подачі звернення (до)', 'class': 'form-control-sm', 'type': 'date'}
        )
    )
    has_decision = forms.ChoiceField(
        choices=HAS_DECISION,
        label='Наявність рішення Апеляційної палати',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select-sm'})
    )
    decision_type = forms.ChoiceField(
        label='Тип рішення Апеляційної палати',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select-sm'})
    )
    history_keywords = forms.CharField(
        label='Ключові слова з історії справи',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Створено колегію', 'class': 'form-control-sm'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        claim_kinds = [('', 'Оберіть тип звернення...')]
        claim_kinds.extend([(x.pk, f"{x.obj_kind.title}: {x.title}") for x in
                            ClaimKind.objects.select_related('obj_kind').order_by('obj_kind__title')])
        self.fields['claim_kind'].choices = claim_kinds

        refusal_reasons = [('', 'Оберіть підставу для оскарження...')]
        refusal_reasons.extend([(x.pk, f"{x.obj_kind.title}: {x.title}") for x in
                                RefusalReason.objects.select_related('obj_kind').order_by('obj_kind__title')])
        self.fields['refusal_reason'].choices = refusal_reasons

        decision_types = [('', 'Оберіть рішення...')]
        decision_types.extend([(x.pk, x.title) for x in DecisionType.objects.order_by('title')])
        self.fields['decision_type'].choices = decision_types

        self.helper = FormHelper()
        self.helper.label_class = "fw-bold"
        self.helper.form_tag = False
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('person_type', css_class='form-group col-md-6 mb-0'),
                Column('person_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'case_number',
            Row(
                Column('case_date_from', css_class='form-group col-md-6 mb-0'),
                Column('case_date_to', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('obj_number', css_class='form-group col-md-6 mb-0'),
                Column('obj_title', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('claim_kind', css_class='form-group col-md-6 mb-0'),
                Column('refusal_reason', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('meeting_date_from', css_class='form-group col-md-6 mb-0'),
                Column('meeting_date_to', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'has_decision',
            'decision_type',
            'history_keywords',
        )

    def clean_person_name(self):
        person_type = self.cleaned_data['person_type']
        if person_type:
            person_name = self.cleaned_data['person_name']
            if not person_name:
                person_name_label = self.fields['person_name'].label
                person_type_label = self.fields['person_type'].label
                raise ValidationError(
                    f'Поле "{person_name_label}" обов\'язкове до заповнення, '
                    f'оскільки заповнене поле "{person_type_label}".'
                )

            return person_name

    def clean(self):
        for value in self.cleaned_data.values():
            if value:
                return
        raise ValidationError(
            'Заповніть хоча б одне поле'
        )

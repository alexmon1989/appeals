from django import forms
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div

from dateutil.relativedelta import relativedelta

from .models import Case
from ..classifiers.models import RefusalReason
from .services.services import case_add_history_action, case_change_stage_step


UserModel = get_user_model()


class ExpertField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name


class CaseUpdateForm(forms.ModelForm):
    goto_2001 = forms.BooleanField(
        required=False,
        label=mark_safe('Перейти до стадії <b>"Досьє заповнено. Очікує на розподіл колегії" (код стадії - 2001)</b>.')
    )
    expert = ExpertField(queryset=UserModel.objects.filter(groups__name='Секретар'), label='Експерт', required=False)
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
        fields = ['refusal_reasons', 'expert']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

        claim_kind = self.instance.claim.claim_kind.title.lower()
        if 'заперечення' in claim_kind:
            self.fields['refusal_reasons'] = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                queryset=RefusalReason.objects.filter(obj_kind=self.instance.claim.obj_kind),
                label='Підстава, з якої оскаржується рішення за запереченням'
            )
        elif 'апеляційна заява' in claim_kind:
            self.fields['refusal_reasons'] = forms.ModelMultipleChoiceField(
                widget=forms.CheckboxSelectMultiple,
                queryset=RefusalReason.objects.filter(obj_kind=self.instance.claim.obj_kind),
                label='Підстава, з якої визнається недійсним охоронний документ за апеляційною заявою',
            )
        else:
            del self.fields['refusal_reasons']

        self.fields['submission_date'].initial = self.instance.claim.submission_date.strftime('%Y-%m-%d')
        self.fields['submission_date'].help_text = 'Недоступне для редагування, оскільки канал надходження звернення - "веб-форма"'
        self.fields['deadline'].initial = (self.instance.claim.submission_date + relativedelta(months=2)).strftime('%Y-%m-%d')
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
        case_add_history_action(self.instance.id, 'Зміна даних справи', self.user.pk)

        # Переход к стадии 2001 - "Досьє заповнено. Очікує на розподіл колегії."
        if self.cleaned_data.get('goto_2001') and self.instance.stage_step.code == 2000:
            case_change_stage_step(self.instance.pk, 2001, self.user.pk)

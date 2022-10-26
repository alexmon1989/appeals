from django import forms

from crispy_forms.helper import FormHelper
from django_select2 import forms as s2forms

from .models import Payment


class CaseNumberWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "case_number__icontains",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.i18n_name = 'uk'


class PaymentUpdateForm(forms.ModelForm):
    """Форма загрузки вторичных документов."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.form_id = "payment-update-form"
        self.helper.label_class = "fw-bold"
        self.helper.field_class = "mb-4"

    class Meta:
        model = Payment
        fields = ['cases']
        widgets = {
            "cases": CaseNumberWidget(
                attrs={
                    'data-minimum-input-length': 0,
                    'data-allow-clear': True,
                    'data-placeholder': 'Введіть номер справи',
                    'data-theme': 'bootstrap-5',
                    'data-container-css-class': '',
                    'data-dropdown-css-class': 'select2--small',
                }
            ),
        }

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.forms import (
    AuthenticationForm, UsernameField
)
from django.utils.translation import gettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from crispy_bootstrap5.bootstrap5 import FloatingField

from .models import User


class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = User
        fields = ('email',)


class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email',)


class CustomAuthenticationForm(AuthenticationForm):

    username = UsernameField(widget=forms.EmailInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'bs-validate p-4 p-md-5 card rounded-xl'
        self.helper.form_method = 'post'
        self.helper.attrs = {'novalidate': True}
        self.helper.layout = Layout(
            FloatingField("username"),
            FloatingField("password", template='registration/_partials/login_form_password_field.html'),
            Div(template='registration/_partials/login_form_bottom.html')
        )

    error_messages = {
        'invalid_login': "Будь ласка, введіть правильні Email адресу та пароль. "
                         "Зауважте, що обидва поля чутливі до регістру.",
        'inactive': _("This account is inactive."),
    }


class CustomPasswordResetForm(PasswordResetForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'bs-validate p-4 p-md-5 card rounded-xl'
        self.helper.attrs = {'novalidate': True}
        self.helper.layout = Layout(
            FloatingField("email"),
            Div(
                Div(
                    Submit('submit', 'Скинути', css_class='w-100 fw-medium'), css_class='col-12 col-md-6'
                ),
                css_class='row'
            )
        )


class CustomSetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'bs-validate p-4 p-md-5 card rounded-xl'
        self.helper.attrs = {'novalidate': True}
        self.helper.layout = Layout(
            FloatingField("new_password1", template='registration/_partials/set_password_form_new_password1_field.html'),
            FloatingField("new_password2"),
            Div(
                Div(
                    Submit('submit', 'Встановити пароль', css_class='w-100 fw-medium'), css_class='col-12 col-md-6'
                ),
                css_class='row'
            )
        )


class AuthFormDSFile(forms.Form):
    """Форма авторизации с помощью файловой ЭЦП."""
    key_file = forms.FileField(label='Файл ключа КЕП')
    cert_file = forms.FileField(label='Файл з сертифікатом', required=False)
    password = forms.CharField(label='Пароль сертифікату', widget=forms.PasswordInput())

from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import resolve_url
from django.conf import settings

from .forms import CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm


class CustomLoginView(SuccessMessageMixin, LoginView):
    """Отображает страницу входа."""
    form_class = CustomAuthenticationForm
    success_message = 'Вхід успішний.'

    def get_success_url(self, *args):
        url = self.get_redirect_url()
        if url:
            return url

        if self.request.user.belongs_to_group('Заявник'):
            return resolve_url('my-applications-list')

        return resolve_url(settings.LOGIN_REDIRECT_URL)


class CustomLogoutView(LogoutView):
    """Разлогинивает пользователя."""
    form_class = CustomAuthenticationForm
    success_message = 'Вихід успішний.'

    def get_next_page(self):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            self.success_message
        )
        return super().get_next_page()


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm

from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import resolve_url, render
from django.conf import settings
from django.http import JsonResponse
import random
import string
import json

from .forms import CustomAuthenticationForm, CustomPasswordResetForm, CustomSetPasswordForm, AuthFormDSFile
from .services import get_certificate


class CustomLoginView(SuccessMessageMixin, LoginView):
    """Отображает страницу входа."""
    form_class = CustomAuthenticationForm
    success_message = 'Вхід успішний.'

    def get_success_url(self, *args):
        url = self.get_redirect_url()
        if url:
            return url

        if self.request.user.belongs_to_group('Заявник'):
            return resolve_url('my-claims-list')

        return resolve_url(settings.LOGIN_REDIRECT_URL)


def login_view_ds_file(request):
    """Страница логина пользователей с помощью файловой ЭЦП."""
    if request.method == 'POST':
        # Проверка валидности ЭЦП
        key_data = json.loads(request.body)
        cert = get_certificate(key_data, request.session['secret'])

        if cert:
            user = authenticate(certificate=cert)
            if user is not None:
                login(request, user)
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    f'Авторизація успішна. Вітаємо, {cert.pszSubjFullName}'
                )
                return JsonResponse({
                    'is_logged': 1
                })
        return JsonResponse({
            'is_logged': 0
        })

    request.session['secret'] = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(32)
    )
    return render(
        request,
        'users/login_ds/index.html',
        {
            'form': AuthFormDSFile(),
        }
    )


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

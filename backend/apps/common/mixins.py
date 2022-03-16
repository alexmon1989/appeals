from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    """Mixin, проверяющий авторизирован ли пользователь."""
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())

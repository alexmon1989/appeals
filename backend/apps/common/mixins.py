from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required


class LoginRequiredMixin(object):
    """Mixin, проверяющий авторизирован ли пользователь."""
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())


class StaffRequiredMixin(object):
    @classmethod
    def as_view(self, *args, **kwargs):
        view = super(StaffRequiredMixin, self).as_view(*args, **kwargs)
        return staff_member_required(view)

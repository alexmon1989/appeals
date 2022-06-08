from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views import View

from ..classifiers import services as classifiers_services
from . import services as filling_services
from ..common.mixins import LoginRequiredMixin


@login_required
def my_applications_list(request):
    """Отображает страницу со списком апелляционных дел."""
    claims = filling_services.get_users_claims_qs(request.user)
    return render(request, 'filling/my_claims_list/index.html', {'claims': claims})


class CreateClaimView(LoginRequiredMixin, View):
    """Отображает страницу создания обращения."""

    template_name = 'filling/create_claim/index.html'

    def get(self, request, *args, **kwargs):
        # Типы объектов
        obj_kinds = classifiers_services.get_obj_kinds_list()

        # Типы обращений
        claim_kinds = classifiers_services.get_claim_kinds(bool_as_int=True)

        # Возможные поля обращений (зависящие от типа)
        claim_fields = filling_services.get_claim_fields(bool_as_int=True)

        return render(
            request,
            self.template_name,
            {
                'obj_kinds': obj_kinds,
                'claim_kinds': claim_kinds,
                'claim_fields': claim_fields,
            }
        )

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST-запрос, создаёт обращение."""
        post_data = request.POST.dict()
        del post_data['csrfmiddlewaretoken']

        claim = filling_services.create_claim(post_data, request.FILES, request.user)

        return JsonResponse({'success': 1, 'claim_id': claim.pk})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from .services import services
from .models import Case


@login_required
def cases_list(request):
    """Отображает страницу со списком апелляционных дел."""
    cases = services.case_get_list(user=request.user)
    return render(request, 'cases/list/index.html', {'cases': cases})


class CaseDetailView(DetailView):
    """Отображает страницу апелляционного дела."""
    model = Case
    template_name = 'cases/detail/index.html'

    def get_queryset(self):
        return services.case_get_list(user=self.request.user)

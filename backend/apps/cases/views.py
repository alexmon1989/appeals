from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Case


@login_required
def cases_list(request):
    cases = Case.objects.select_related('obj_kind', 'claim_kind')

    return render(request, 'cases/list/index.html', {'cases': cases})

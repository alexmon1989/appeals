from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def cases_list(request):
    return render(request, 'cases/list/index.html')

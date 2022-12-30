from django.shortcuts import render
from .forms import StatForm
from .services import stat_get_data


def index(request):
    context = {}
    if request.GET:
        context['form'] = StatForm(request.GET)
        if context['form'].is_valid():
            context['data'] = stat_get_data(
                request.GET['stat_type'],
                request.GET['date_from'],
                request.GET['date_to']
            )
    else:
        context['form'] = StatForm()

    return render(
        request,
        template_name='stats/index/index.html',
        context=context
    )

from django.shortcuts import render
from .forms import SearchForm
from .services import search


def index(request):
    """Отображает страницу поиска."""
    context = {}
    if request.GET:
        context['form'] = SearchForm(request.GET)
        if context['form'].is_valid():
            context['results'] = search(request.GET)
    else:
        context['form'] = SearchForm()

    return render(
        request,
        template_name='search/index/index.html',
        context=context
    )

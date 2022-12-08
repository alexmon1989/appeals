from django.shortcuts import render
from .forms import SearchForm


def index(request):
    form = SearchForm()
    return render(
        request,
        template_name='search/index/index.html',
        context={'form': form}
    )

from django.shortcuts import render
from django.views.generic.list import ListView
from apps.cases.models import Case


class CaseListView(ListView):

    model = Case
    template_name = 'archive/list/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

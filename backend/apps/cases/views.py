from django.shortcuts import render


def cases_list(request):
    return render(request, 'cases/list/index.html')

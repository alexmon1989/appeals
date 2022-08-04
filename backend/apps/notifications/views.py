from django.shortcuts import render


def list_index(request):
    return render(request, template_name='notifications/list/index.html')

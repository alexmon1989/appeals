from django.shortcuts import render, reverse
from django.db.models import Count
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework import viewsets, permissions

from .serializers import PaymentsSerializer
from .models import Payment
from .forms import PaymentUpdateForm
from apps.common.mixins import LoginRequiredMixin


@login_required
def payments_list(request):
    """Отображает страницу с платежами."""
    return render(request, 'payments/list/index.html')


class PaymentsViewSet(viewsets.ReadOnlyModelViewSet):
    """Возвращает JSON с платежами."""
    serializer_class = PaymentsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Payment.objects.order_by('-created_at').annotate(num_cases=Count('cases'))


class PaymentUpdateView(LoginRequiredMixin, UpdateView):
    """Отображает страницу редактирования платежа."""
    model = Payment
    template_name = 'payments/update/index.html'
    form_class = PaymentUpdateForm

    def get_success_url(self):
        messages.success(self.request, 'Дані збережено')
        return reverse('payments-update', kwargs={'pk': self.kwargs['pk']})

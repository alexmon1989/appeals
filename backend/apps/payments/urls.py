from django.urls import path

from . import views


urlpatterns = [
    path('', views.payments_list, name='payments-list'),
    path('list.json', views.PaymentsViewSet.as_view({'get': 'list'}), name='payments-list-json'),
    path('update/<int:pk>', views.PaymentUpdateView.as_view(), name='payments-update'),
]

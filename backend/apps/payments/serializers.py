from django.template.loader import render_to_string

from rest_framework import serializers
from .models import Payment


class PaymentsSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M:%S')
    payment_date = serializers.DateField(format='%d.%m.%Y')
    num_cases = serializers.ReadOnlyField()
    actions = serializers.SerializerMethodField()

    def get_actions(self, payment: Payment):
        return render_to_string(
            'payments/list/_partials/actions.html',
            {
                'payment': payment,
            }
        )

    class Meta:
        model = Payment
        fields = [
            'title',
            'value',
            'payment_date',
            'created_at',
            'num_cases',
            'actions'
        ]

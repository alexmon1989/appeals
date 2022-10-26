from django.contrib import admin

from .models import Payment, PaymentCase


class PaymentCaseInline(admin.TabularInline):
    model = PaymentCase
    extra = 0


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    inlines = (PaymentCaseInline,)
    list_display = (
        'title',
        'value',
        'payment_date',
        'bop_id',
        'created_at',
        'updated_at'
    )
    search_fields = (
        'title',
    )

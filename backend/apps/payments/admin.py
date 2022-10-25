from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('title', 'bop_id', 'case', 'approved_by', 'approved_at', 'created_at')

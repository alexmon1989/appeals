from django.contrib import admin
from django.contrib.admin import display
from .models import ClaimField
from .forms import ClaimFieldForm


@admin.register(ClaimField)
class Admin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'get_obj_kind', 'claim_kind', 'field_type', 'stage', 'created_at', 'updated_at')
    form = ClaimFieldForm
    list_filter = ('stage', 'claim_kind__obj_kind__title')
    search_fields = ('title',)

    def get_queryset(self, request):
        return ClaimField.objects.select_related('claim_kind', 'claim_kind__obj_kind')

    @display(ordering='claim_kind__obj_kind__title', description="Вид об'єкта")
    def get_obj_kind(self, obj):
        return obj.claim_kind.obj_kind.title

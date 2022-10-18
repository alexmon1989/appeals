from django.contrib import admin
from .models import DocumentType, ObjKind, ClaimKind, RefusalReason, Speciality


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'direction', 'origin', 'code', 'created_at', 'updated_at')
    list_filter = ('direction', 'origin',)
    search_fields = ('title',)
    filter_horizontal = ('claim_kinds',)
    list_editable = ('code',)

    def get_queryset(self, request):
        return DocumentType.objects.prefetch_related('claim_kinds', 'claim_kinds__obj_kind')


@admin.register(ClaimKind)
class ClaimKindAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'obj_kind', 'third_person', 'created_at', 'updated_at')
    list_filter = ('obj_kind',)
    list_editable = ('third_person',)


@admin.register(ObjKind)
class ObjKindAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'sis_id', 'created_at', 'updated_at')
    list_editable = ('sis_id',)


@admin.register(RefusalReason)
class RefusalReasonAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'obj_kind', 'created_at', 'updated_at')

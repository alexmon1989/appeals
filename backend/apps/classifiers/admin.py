from django.contrib import admin
from .models import DocumentType, ObjKind, ClaimKind, RefusalReason, DecisionType, ClaimPersonType, StopReason


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
    list_display = ('title', 'abbr', 'obj_kind', 'third_person', 'created_at', 'updated_at')
    list_filter = ('obj_kind',)
    list_editable = ('third_person', 'abbr',)


@admin.register(ObjKind)
class ObjKindAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'abbr', 'sis_id', 'created_at', 'updated_at')
    list_editable = ('sis_id', 'abbr',)


@admin.register(RefusalReason)
class RefusalReasonAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'obj_kind', 'created_at', 'updated_at')


@admin.register(ClaimPersonType)
class ClaimPersonTypeAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'created_at', 'updated_at')


@admin.register(DecisionType)
class DecisionTypeAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'created_at', 'updated_at')
    filter_horizontal = ('claim_kinds',)

    def get_queryset(self, request):
        return DecisionType.objects.prefetch_related('claim_kinds', 'claim_kinds__obj_kind')


@admin.register(StopReason)
class StopReasonAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'created_at', 'updated_at')

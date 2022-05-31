from django.contrib import admin
from .models import DocumentType, DocumentName, ObjKind, ClaimKind


@admin.register(DocumentType, DocumentName)
class Admin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'created_at', 'updated_at')


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

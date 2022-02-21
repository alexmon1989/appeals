from django.contrib import admin
from .models import DocumentType, DocumentName, ObjKind, ClaimKind


@admin.register(DocumentType, DocumentName, ObjKind, ClaimKind)
class Admin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('title', 'created_at', 'updated_at')

from django.contrib import admin
from .models import Case, CollegiumMembership, Document, Sign, DocumentTemplate
from .services import services


class CollegiumMembershipInline(admin.TabularInline):
    model = CollegiumMembership
    extra = 0


class DocumentInline(admin.StackedInline):
    model = Document
    extra = 0


class SignInline(admin.StackedInline):
    model = Sign
    extra = 0


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    ordering = ('case_number',)
    inlines = (CollegiumMembershipInline, DocumentInline)
    list_display = (
        'case_number',
    )
    search_fields = (
        'case_number',
    )

    def get_queryset(self, request):
        return services.case_get_list()


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    inlines = (SignInline,)


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'title',
    )

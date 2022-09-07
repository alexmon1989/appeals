from django.contrib import admin
from .models import Case, CollegiumMembership, Document, Sign, CaseStage, CaseStageStep
from .services import case_services


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
        return case_services.case_get_all_qs()


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    inlines = (SignInline,)


@admin.register(CaseStage)
class CaseStageAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'number',
    )


@admin.register(CaseStageStep)
class CaseStageItemAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'stage',
        'code',
    )

    def get_queryset(self, request):
        return CaseStageStep.objects.select_related('stage')

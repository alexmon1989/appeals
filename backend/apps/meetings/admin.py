from django.contrib import admin
from django.contrib.admin import display
from .models import Meeting, Absence, Invitation
from .forms import AbsenceAdminForm, InvitationAdminForm


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('case', 'datetime', 'created_at', 'updated_at')
    search_fields = ('case__case_number',)

    def get_queryset(self, request):
        return Meeting.objects.select_related('case')


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    ordering = ('pk',)
    list_display = ('get_user', 'get_meeting_datetime', 'accepted_at', 'rejected_at', 'created_at', 'updated_at')
    search_fields = ('user__last_name', 'meeting__case__case_number')
    form = InvitationAdminForm

    def get_queryset(self, request):
        return Invitation.objects.select_related('user', 'meeting', 'meeting__case')

    @display(ordering='meeting__datetime', description="Дата та час засідання")
    def get_meeting_datetime(self, obj):
        return obj.meeting.datetime

    @display(ordering='user__last_name', description="Співробітник АП")
    def get_user(self, obj):
        return obj.user.get_full_name_initials()


@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    ordering = ('-pk',)
    list_display = ('get_user', 'date_from', 'date_to', 'created_at', 'updated_at')
    search_fields = ('user__last_name',)
    form = AbsenceAdminForm

    def get_queryset(self, request):
        return Absence.objects.select_related('user')

    @display(ordering='user__last_name', description="Співробітник АП")
    def get_user(self, obj):
        return obj.user.get_full_name_initials()

from django.contrib import admin
from .models import Case


@admin.register(Case)
class Admin(admin.ModelAdmin):
    ordering = ('pk',)

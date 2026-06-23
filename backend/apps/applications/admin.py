from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "status", "applied_date")
    list_filter = ("status",)

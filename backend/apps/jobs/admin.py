from django.contrib import admin

from .models import Job, JobEmbedding, SavedJob


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "is_remote", "experience_level")
    list_filter = ("is_remote", "experience_level", "is_active")
    search_fields = ("title", "company")


@admin.register(JobEmbedding)
class JobEmbeddingAdmin(admin.ModelAdmin):
    list_display = ("job", "model", "created_at")


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "saved_at")

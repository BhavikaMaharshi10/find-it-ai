from django.contrib import admin

from .models import Resume, ResumeEmbedding


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ("original_filename", "user", "is_active", "created_at")
    list_filter = ("is_active",)


@admin.register(ResumeEmbedding)
class ResumeEmbeddingAdmin(admin.ModelAdmin):
    list_display = ("resume", "model", "created_at")

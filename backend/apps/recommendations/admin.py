from django.contrib import admin

from .models import AILog, Recommendation, SkillGap


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "match_score", "is_viewed")
    list_filter = ("is_viewed",)


@admin.register(SkillGap)
class SkillGapAdmin(admin.ModelAdmin):
    list_display = ("recommendation", "skill_name", "severity")


@admin.register(AILog)
class AILogAdmin(admin.ModelAdmin):
    list_display = ("user", "service", "action", "tokens_used", "created_at")

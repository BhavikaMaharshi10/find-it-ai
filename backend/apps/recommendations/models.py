import uuid

from django.conf import settings
from django.db import models

from apps.jobs.models import Job


class Recommendation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recommendations",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="recommendations",
    )
    match_score = models.FloatField()
    reasoning = models.TextField()
    missing_skills = models.JSONField(default=list, blank=True)
    strengths = models.JSONField(default=list, blank=True)
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recommendations"
        unique_together = ["user", "job"]
        ordering = ["-match_score", "-created_at"]

    def __str__(self):
        return f"{self.job.title} — {self.match_score}%"


class SkillGap(models.Model):
    SEVERITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recommendation = models.ForeignKey(
        Recommendation,
        on_delete=models.CASCADE,
        related_name="skill_gaps",
    )
    skill_name = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="medium")
    learning_suggestion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "skill_gaps"

    def __str__(self):
        return f"{self.skill_name} ({self.severity})"


class AILog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_logs",
        null=True,
        blank=True,
    )
    service = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    tokens_used = models.IntegerField(default=0)
    cost_usd = models.FloatField(default=0.0)
    duration_ms = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_logs"
        ordering = ["-created_at"]

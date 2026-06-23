import uuid

from django.conf import settings
from django.db import models

from apps.jobs.models import Job


class Application(models.Model):
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("interview_scheduled", "Interview Scheduled"),
        ("interview_completed", "Interview Completed"),
        ("rejected", "Rejected"),
        ("offer_received", "Offer Received"),
        ("accepted", "Accepted"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="applied")
    notes = models.TextField(blank=True)
    applied_date = models.DateField(auto_now_add=True)
    interview_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "applications"
        unique_together = ["user", "job"]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.email} → {self.job.title} ({self.status})"

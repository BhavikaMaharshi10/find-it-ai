import uuid

from django.conf import settings
from django.db import models

if "test" in settings.SETTINGS_MODULE:
    _EmbeddingField = lambda **kw: models.JSONField(default=list, blank=True)  # noqa: E731
else:
    from pgvector.django import HnswIndex, VectorField

    _EmbeddingField = lambda **kw: VectorField(dimensions=settings.EMBEDDING_DIMENSIONS)  # noqa: E731


class Job(models.Model):
    EXPERIENCE_LEVELS = [
        ("junior", "Junior"),
        ("mid", "Mid-Level"),
        ("senior", "Senior"),
        ("lead", "Lead"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    is_remote = models.BooleanField(default=False)
    experience_level = models.CharField(
        max_length=20, choices=EXPERIENCE_LEVELS, default="mid"
    )
    required_skills = models.JSONField(default=list, blank=True)
    preferred_skills = models.JSONField(default=list, blank=True)
    salary_range = models.CharField(max_length=100, blank=True)
    employment_type = models.CharField(max_length=50, default="full-time")
    source_url = models.URLField(blank=True)
    source = models.CharField(max_length=50, default="seed", db_index=True)
    external_id = models.CharField(max_length=255, blank=True, default="", db_index=True)
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "jobs"
        ordering = ["-posted_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_id"],
                condition=models.Q(external_id__gt=""),
                name="jobs_unique_source_external_id",
            ),
        ]

    def __str__(self):
        return f"{self.title} at {self.company}"


class JobEmbedding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.OneToOneField(
        Job,
        on_delete=models.CASCADE,
        related_name="embedding",
    )
    embedding = _EmbeddingField()
    model = models.CharField(max_length=100, default="gemini-embedding-001")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "job_embeddings"
        indexes = (
            [
                HnswIndex(
                    name="job_embedding_hnsw_idx",
                    fields=["embedding"],
                    opclasses=["vector_cosine_ops"],
                ),
            ]
            if "test" not in settings.SETTINGS_MODULE
            else []
        )


class SavedJob(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_jobs",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    notes = models.TextField(blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "saved_jobs"
        unique_together = ["user", "job"]
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.user.email} saved {self.job.title}"

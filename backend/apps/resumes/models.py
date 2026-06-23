import uuid

from django.conf import settings
from django.db import models

if "test" in settings.SETTINGS_MODULE:
    _EmbeddingField = lambda **kw: models.JSONField(default=list, blank=True)  # noqa: E731
else:
    from pgvector.django import HnswIndex, VectorField

    _EmbeddingField = lambda **kw: VectorField(dimensions=settings.EMBEDDING_DIMENSIONS)  # noqa: E731


def resume_upload_path(instance, filename):
    return f"resumes/{instance.user_id}/{filename}"


class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resumes",
    )
    file = models.FileField(upload_to=resume_upload_path)
    original_filename = models.CharField(max_length=255)
    raw_text = models.TextField(blank=True)
    structured_data = models.JSONField(default=dict, blank=True)
    skills = models.JSONField(default=list, blank=True)
    education = models.JSONField(default=list, blank=True)
    work_experience = models.JSONField(default=list, blank=True)
    projects = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    ai_summary = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resumes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.original_filename} ({self.user.email})"


class ResumeEmbedding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.OneToOneField(
        Resume,
        on_delete=models.CASCADE,
        related_name="embedding",
    )
    embedding = _EmbeddingField()
    model = models.CharField(max_length=100, default="gemini-embedding-001")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "resume_embeddings"
        indexes = (
            [
                HnswIndex(
                    name="resume_embedding_hnsw_idx",
                    fields=["embedding"],
                    opclasses=["vector_cosine_ops"],
                ),
            ]
            if "test" not in settings.SETTINGS_MODULE
            else []
        )

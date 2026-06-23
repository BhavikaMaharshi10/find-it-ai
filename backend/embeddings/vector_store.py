"""Vector similarity search utilities."""
from pgvector.django import CosineDistance

from apps.jobs.models import JobEmbedding


def cosine_similarity_search(query_embedding, top_k=10, filters=None):
    qs = JobEmbedding.objects.annotate(
        distance=CosineDistance("embedding", query_embedding)
    ).filter(job__is_active=True)

    if filters:
        if filters.get("is_remote") is not None:
            qs = qs.filter(job__is_remote=filters["is_remote"])
        if filters.get("experience_level"):
            qs = qs.filter(job__experience_level=filters["experience_level"])

    return qs.order_by("distance")[:top_k]

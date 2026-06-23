"""Google Gemini embedding generation and storage."""
import time

from django.conf import settings

from apps.jobs.models import JobEmbedding
from apps.recommendations.models import AILog
from apps.resumes.models import ResumeEmbedding
from core.services import BaseService
from utils.gemini_client import generate_embedding, generate_embeddings_batch


class EmbeddingService(BaseService):
    def generate_embedding(self, text: str) -> list[float]:
        start = time.time()
        embedding = generate_embedding(text)
        self.logger.info("Generated embedding in %.2fms", (time.time() - start) * 1000)
        return embedding

    def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        return generate_embeddings_batch(texts)

    def store_resume_embedding(self, resume_id, embedding: list[float], user=None) -> None:
        ResumeEmbedding.objects.update_or_create(
            resume_id=resume_id,
            defaults={
                "embedding": embedding,
                "model": settings.GEMINI_EMBEDDING_MODEL,
            },
        )

    def store_job_embedding(self, job_id, embedding: list[float]) -> None:
        JobEmbedding.objects.update_or_create(
            job_id=job_id,
            defaults={
                "embedding": embedding,
                "model": settings.GEMINI_EMBEDDING_MODEL,
            },
        )

    def log_ai_call(self, user, service, action, request_data, response_data, tokens=0):
        AILog.objects.create(
            user=user,
            service=service,
            action=action,
            request_data=request_data,
            response_data=response_data,
            tokens_used=tokens,
        )

"""RAG pipeline: ingest, retrieve, generate."""
import json

from core.services import BaseService
from embeddings.vector_store import cosine_similarity_search
from services.embedding import EmbeddingService
from services.learning import LearningRecommendationService
from services.recommendation import RecommendationService
from utils.gemini_client import chat_completion_json


class RAGService(BaseService):
    def __init__(self):
        super().__init__()
        self.embedding_service = EmbeddingService()
        self.recommendation_service = RecommendationService()
        self.learning_service = LearningRecommendationService()

    def ingest(self, content: str, content_type: str, entity_id) -> None:
        embedding = self.embedding_service.generate_embedding(content)
        if content_type == "resume":
            self.embedding_service.store_resume_embedding(entity_id, embedding)
        elif content_type == "job":
            self.embedding_service.store_job_embedding(entity_id, embedding)

    def retrieve(self, query: str, top_k: int = 5, filters=None) -> list:
        query_embedding = self.embedding_service.generate_embedding(query)
        results = cosine_similarity_search(query_embedding, top_k, filters)
        return [
            {
                "job_id": str(je.job.id),
                "title": je.job.title,
                "company": je.job.company,
                "description": je.job.description[:500],
                "distance": float(je.distance),
            }
            for je in results
        ]

    def generate(self, query: str, context: list) -> dict:
        context_text = json.dumps(context)[:4000]
        prompt = f"""Based on the following job context, answer the user's query.

Context:
{context_text}

User Query: {query}

Provide a helpful JSON response with recommendations and advice."""

        try:
            return chat_completion_json(
                [{"role": "user", "content": prompt}],
                temperature=0.4,
            )
        except Exception as e:
            self.logger.error("RAG generation failed: %s", e)
            return {"message": "Unable to generate response.", "recommendations": context}

    def run_pipeline(self, user, query: str) -> dict:
        from apps.resumes.models import Resume

        resume = Resume.objects.filter(user=user, is_active=True).first()
        filters = {}
        retrieved = self.retrieve(query, top_k=5, filters=filters)
        generated = self.generate(query, retrieved)

        recommendations = []
        if resume:
            recommendations = self.recommendation_service.find_similar_jobs(user, top_k=5)

        skill_gaps = []
        if recommendations:
            skill_gaps = recommendations[0].get("missing_skills", [])

        learning = self.learning_service.generate_learning_roadmap(
            skill_gaps,
            {"skills": resume.skills if resume else [], "summary": resume.ai_summary if resume else ""},
        )

        return {
            "query": query,
            "retrieved_jobs": retrieved,
            "generated_response": generated,
            "recommendations": recommendations,
            "learning_roadmap": learning,
        }

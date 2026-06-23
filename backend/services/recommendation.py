"""Job recommendation engine with vector similarity."""
import json

from pgvector.django import CosineDistance

from apps.jobs.models import Job, JobEmbedding
from apps.recommendations.models import Recommendation, SkillGap
from apps.resumes.models import Resume
from core.services import BaseService
from prompts.templates import JOB_MATCH_PROMPT, SKILL_GAP_PROMPT
from services.embedding import EmbeddingService
from utils.gemini_client import chat_completion_json, is_gemini_configured


class RecommendationService(BaseService):
    def __init__(self):
        super().__init__()
        self.embedding_service = EmbeddingService()

    def get_active_resume(self, user):
        return Resume.objects.filter(user=user, is_active=True).first()

    def find_similar_jobs(self, user, top_k: int = 10) -> list[dict]:
        resume = self.get_active_resume(user)
        if not resume or not hasattr(resume, "embedding"):
            return []

        resume_embedding = resume.embedding.embedding
        job_embeddings = (
            JobEmbedding.objects.annotate(
                distance=CosineDistance("embedding", resume_embedding)
            )
            .filter(job__is_active=True)
            .order_by("distance")[:top_k]
        )

        results = []
        for je in job_embeddings:
            score = max(0, min(100, (1 - je.distance) * 100))
            job = je.job
            user_skills = [s.lower() for s in (resume.skills or [])]
            job_skills = [s.lower() for s in (job.required_skills or [])]
            missing = self.identify_skill_gaps(user_skills, job_skills)
            reasoning = self._generate_reasoning(resume, job, score, user)

            rec, _ = Recommendation.objects.update_or_create(
                user=user,
                job=job,
                defaults={
                    "match_score": round(score, 1),
                    "reasoning": reasoning,
                    "missing_skills": missing,
                    "strengths": self._matching_skills(user_skills, job_skills),
                },
            )
            SkillGap.objects.filter(recommendation=rec).delete()
            for skill in missing:
                SkillGap.objects.create(
                    recommendation=rec,
                    skill_name=skill,
                    severity="high" if skill in (job.required_skills or [])[:3] else "medium",
                )
            results.append(self._serialize_recommendation(rec))

        return results

    def calculate_match_score(self, resume_embedding, job_embedding) -> float:
        from numpy import dot
        from numpy.linalg import norm

        a = resume_embedding
        b = job_embedding
        if not a or not b:
            return 0.0
        return float(dot(a, b) / (norm(a) * norm(b)) * 100)

    def identify_skill_gaps(self, user_skills: list, job_skills: list) -> list:
        user_set = {s.lower().strip() for s in user_skills}
        return [s for s in job_skills if s.lower().strip() not in user_set]

    def _matching_skills(self, user_skills, job_skills):
        user_set = {s.lower() for s in user_skills}
        return [s for s in job_skills if s.lower() in user_set]

    def _generate_reasoning(self, resume, job, score, user) -> str:
        if not is_gemini_configured():
            return (
                f"Match score of {score:.0f}% based on skill overlap between "
                f"your resume and {job.title} at {job.company}."
            )
        try:
            result = chat_completion_json(
                [{"role": "user", "content": JOB_MATCH_PROMPT.format(
                    candidate_data=json.dumps({
                        "skills": resume.skills,
                        "summary": resume.ai_summary,
                    }),
                    job_data=json.dumps({
                        "title": job.title,
                        "company": job.company,
                        "required_skills": job.required_skills,
                        "description": job.description[:1000],
                    }),
                )}],
                temperature=0.3,
            )
            return result.get("reasoning", f"Strong match at {score:.0f}% for {job.title}.")
        except Exception:
            return f"Strong alignment with {job.title} requirements ({score:.0f}% match)."

    def _serialize_recommendation(self, rec) -> dict:
        return {
            "id": str(rec.id),
            "job_title": rec.job.title,
            "company": rec.job.company,
            "score": rec.match_score,
            "missing_skills": rec.missing_skills,
            "reasoning": rec.reasoning,
            "job_id": str(rec.job.id),
        }

    def analyze_skill_gaps(self, user_skills, job_skills, user=None) -> dict:
        if not is_gemini_configured():
            missing = self.identify_skill_gaps(user_skills, job_skills)
            return {
                "missing_skills": missing,
                "matching_skills": self._matching_skills(user_skills, job_skills),
                "gap_severity": "medium" if missing else "low",
            }
        try:
            return chat_completion_json(
                [{"role": "user", "content": SKILL_GAP_PROMPT.format(
                    candidate_skills=", ".join(user_skills),
                    job_requirements=", ".join(job_skills),
                )}],
            )
        except Exception:
            missing = self.identify_skill_gaps(user_skills, job_skills)
            return {"missing_skills": missing, "matching_skills": [], "gap_severity": "medium"}

"""Job recommendation engine with vector similarity."""
import json

from django.utils import timezone
from pgvector.django import CosineDistance

from apps.jobs.models import Job, JobEmbedding
from apps.recommendations.models import Recommendation, SkillGap
from apps.resumes.models import Resume
from core.services import BaseService
from prompts.templates import JOB_MATCH_PROMPT, SKILL_GAP_PROMPT
from services.embedding import EmbeddingService
from services.job_ingestion import JobIngestionService, NormalizedJob, normalized_to_dict
from utils.gemini_client import chat_completion_json, is_gemini_configured

LIVE_EMBED_CANDIDATE_LIMIT = 50


class RecommendationService(BaseService):
    def __init__(self):
        super().__init__()
        self.embedding_service = EmbeddingService()

    def get_active_resume(self, user):
        return Resume.objects.filter(user=user, is_active=True).first()

    def _get_resume_embedding(self, resume):
        try:
            embedding = resume.embedding.embedding
        except Exception:
            return None
        if embedding is None:
            return None
        try:
            return embedding if len(embedding) > 0 else None
        except TypeError:
            return embedding

    def find_live_matches(self, user, top_k: int = 10, refresh: bool = False) -> list[dict]:
        """Match the user's resume against live job postings (not stored in DB)."""
        resume = self.get_active_resume(user)
        if not resume:
            return []

        live_jobs = JobIngestionService()._get_live_pool(refresh=refresh)
        if not live_jobs:
            return []

        user_skills = resume.skills or []
        ranked_candidates = sorted(
            live_jobs,
            key=lambda job: self._skill_overlap_score(user_skills, job.required_skills),
            reverse=True,
        )
        candidates = ranked_candidates[: max(top_k * 5, LIVE_EMBED_CANDIDATE_LIMIT)]

        resume_embedding = self._get_resume_embedding(resume)

        if resume_embedding is not None and is_gemini_configured():
            ranked = self._rank_live_by_embedding(resume_embedding, candidates)
            if ranked:
                selected = ranked[:top_k]
            else:
                selected = [
                    (
                        self._skill_overlap_score(user_skills, job.required_skills),
                        job,
                    )
                    for job in candidates[:top_k]
                ]
        else:
            selected = [
                (
                    self._skill_overlap_score(user_skills, job.required_skills),
                    job,
                )
                for job in candidates[:top_k]
            ]

        results = [
            self._build_live_recommendation(resume, job, score, user)
            for score, job in selected
        ]

        return results

    def find_similar_jobs(self, user, top_k: int = 10) -> list[dict]:
        """Legacy DB-backed matching (used by RAG pipeline)."""
        resume = self.get_active_resume(user)
        if not resume:
            return []

        resume_embedding = self._get_resume_embedding(resume)
        if resume_embedding is None:
            return []
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
        from numpy import asarray, dot
        from numpy.linalg import norm

        try:
            a = asarray(resume_embedding, dtype=float)
            b = asarray(job_embedding, dtype=float)
        except (TypeError, ValueError):
            return 0.0

        if a.size == 0 or b.size == 0:
            return 0.0

        denom = float(norm(a) * norm(b))
        if denom == 0.0:
            return 0.0

        return float(dot(a, b) / denom * 100)

    def identify_skill_gaps(self, user_skills: list, job_skills: list) -> list:
        user_set = {s.lower().strip() for s in user_skills}
        return [s for s in job_skills if s.lower().strip() not in user_set]

    def _skill_overlap_score(self, user_skills: list, job_skills: list) -> float:
        user_set = {s.lower().strip() for s in user_skills if s}
        job_set = {s.lower().strip() for s in job_skills if s}
        if not job_set:
            return 35.0
        overlap = len(user_set & job_set)
        return min(100.0, (overlap / len(job_set)) * 100)

    def _matching_skills(self, user_skills, job_skills):
        user_set = {s.lower() for s in user_skills}
        return [s for s in job_skills if s.lower() in user_set]

    def _job_embed_text(self, job: NormalizedJob) -> str:
        return (
            f"{job.title} at {job.company}. {job.description[:4000]} "
            f"Skills: {', '.join(job.required_skills or [])}"
        )

    def _rank_live_by_embedding(
        self,
        resume_embedding,
        jobs: list[NormalizedJob],
    ) -> list[tuple[float, NormalizedJob]]:
        texts = [self._job_embed_text(job) for job in jobs]
        try:
            embeddings = self.embedding_service.generate_embeddings_batch(texts)
        except Exception as exc:
            self.logger.warning("Live embedding ranking failed, using skill scores: %s", exc)
            return []

        ranked: list[tuple[float, NormalizedJob]] = []
        for job, job_embedding in zip(jobs, embeddings, strict=False):
            score = self.calculate_match_score(resume_embedding, job_embedding)
            ranked.append((score, job))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return ranked

    def _build_live_recommendation(
        self,
        resume,
        job: NormalizedJob,
        score: float,
        user,
    ) -> dict:
        user_skills = [s.lower() for s in (resume.skills or [])]
        job_skills = job.required_skills or []
        missing = self.identify_skill_gaps(user_skills, job_skills)
        strengths = self._matching_skills(user_skills, job_skills)
        reasoning = self._generate_reasoning_live(resume, job, score)

        return {
            "id": f"live:{job.source}:{job.external_id}",
            "job": normalized_to_dict(job),
            "match_score": round(score, 1),
            "reasoning": reasoning,
            "missing_skills": missing,
            "strengths": strengths,
            "is_viewed": False,
            "created_at": timezone.now().isoformat(),
        }

    def _generate_reasoning_live(self, resume, job: NormalizedJob, score: float) -> str:
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

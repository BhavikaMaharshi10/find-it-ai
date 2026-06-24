"""Service layer unit tests."""
import pytest

from services.learning import LearningRecommendationService
from services.recommendation import RecommendationService
from services.job_ingestion import NormalizedJob


class TestRecommendationService:
    def test_identify_skill_gaps(self):
        service = RecommendationService()
        gaps = service.identify_skill_gaps(
            ["python", "react", "django"],
            ["Python", "Docker", "AWS"],
        )
        assert "Docker" in gaps or "docker" in [g.lower() for g in gaps]

    def test_matching_skills(self):
        service = RecommendationService()
        matches = service._matching_skills(
            ["python", "react"],
            ["Python", "Docker"],
        )
        assert "Python" in matches

    def test_calculate_match_score_with_vectors(self):
        service = RecommendationService()
        score = service.calculate_match_score([1.0, 0.0], [1.0, 0.0])
        assert score == 100.0

        empty_score = service.calculate_match_score([], [1.0, 0.0])
        assert empty_score == 0.0
        service = RecommendationService()
        score = service._skill_overlap_score(
            ["python", "react", "docker"],
            ["Python", "Docker", "AWS"],
        )
        assert score > 0

    def test_find_live_matches_uses_live_pool(self, monkeypatch):
        from types import SimpleNamespace

        live_job = NormalizedJob(
            source="remotive",
            external_id="1",
            title="Senior Python Developer",
            company="Acme",
            description="Build APIs with Python and React",
            location="Remote",
            is_remote=True,
            experience_level="senior",
            required_skills=["Python", "React", "Docker"],
            salary_range="",
            employment_type="full-time",
            source_url="https://example.com/job/1",
            posted_at=None,
        )

        monkeypatch.setattr(
            "services.recommendation.JobIngestionService._get_live_pool",
            lambda self, refresh=False: [live_job],
        )

        resume = SimpleNamespace(skills=["Python", "React"], ai_summary="")
        service = RecommendationService()
        monkeypatch.setattr(service, "get_active_resume", lambda user: resume)

        results = service.find_live_matches(SimpleNamespace(), top_k=5)
        assert len(results) == 1
        assert results[0]["job"]["title"] == "Senior Python Developer"
        assert results[0]["id"].startswith("live:")


class TestLearningService:
    def test_fallback_roadmap(self):
        service = LearningRecommendationService()
        roadmap = service._fallback_roadmap(["Docker", "AWS"])
        assert len(roadmap["courses"]) == 2
        assert roadmap["timeline"]

    def test_empty_gaps(self):
        service = LearningRecommendationService()
        result = service.generate_learning_roadmap([], {})
        assert result["roadmap"] == []

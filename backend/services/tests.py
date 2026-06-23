"""Service layer unit tests."""
import pytest

from services.learning import LearningRecommendationService
from services.recommendation import RecommendationService


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

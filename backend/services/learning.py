"""Learning recommendations and career guidance."""
import json

from core.services import BaseService
from prompts.templates import LEARNING_ROADMAP_PROMPT
from utils.gemini_client import chat_completion_json, is_gemini_configured


class LearningRecommendationService(BaseService):
    def generate_learning_roadmap(self, skill_gaps: list, user_profile: dict) -> dict:
        if not skill_gaps:
            return {
                "roadmap": [],
                "courses": [],
                "certifications": [],
                "timeline": "No skill gaps identified.",
            }

        if not is_gemini_configured():
            return self._fallback_roadmap(skill_gaps)

        try:
            return chat_completion_json(
                [{"role": "user", "content": LEARNING_ROADMAP_PROMPT.format(
                    skill_gaps=", ".join(skill_gaps),
                    profile_data=json.dumps(user_profile)[:2000],
                )}],
                temperature=0.4,
            )
        except Exception as e:
            self.logger.error("Learning roadmap failed: %s", e)
            return self._fallback_roadmap(skill_gaps)

    def recommend_courses(self, skill_gaps: list) -> list:
        roadmap = self.generate_learning_roadmap(skill_gaps, {})
        return roadmap.get("courses", [])

    def recommend_certifications(self, skill_gaps: list) -> list:
        roadmap = self.generate_learning_roadmap(skill_gaps, {})
        return roadmap.get("certifications", [])

    def _fallback_roadmap(self, skill_gaps: list) -> dict:
        courses = [
            {
                "title": f"Learn {skill}",
                "platform": "Coursera",
                "url": f"https://coursera.org/search?query={skill}",
                "skill": skill,
            }
            for skill in skill_gaps[:5]
        ]
        return {
            "roadmap": [
                {"step": i + 1, "skill": s, "description": f"Master {s}", "estimated_weeks": 4}
                for i, s in enumerate(skill_gaps[:5])
            ],
            "courses": courses,
            "certifications": [
                {"name": f"{s} Certification", "provider": "Industry Standard", "skill": s}
                for s in skill_gaps[:3]
            ],
            "timeline": f"{len(skill_gaps) * 4} weeks estimated",
        }

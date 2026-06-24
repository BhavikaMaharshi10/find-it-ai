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
            result = chat_completion_json(
                [{"role": "user", "content": LEARNING_ROADMAP_PROMPT.format(
                    skill_gaps=", ".join(skill_gaps),
                    profile_data=json.dumps(user_profile)[:2000],
                )}],
                temperature=0.4,
            )
            return self._normalize_roadmap(result, skill_gaps)
        except Exception as e:
            self.logger.error("Learning roadmap failed: %s", e)
            return self._fallback_roadmap(skill_gaps)

    def _normalize_roadmap(self, data: dict, skill_gaps: list) -> dict:
        """Ensure roadmap response matches the expected API shape."""
        roadmap = data.get("roadmap") or data.get("learning_roadmap") or data.get("steps") or []
        if isinstance(roadmap, dict):
            roadmap = roadmap.get("steps", [])

        normalized = []
        for i, step in enumerate(roadmap):
            if isinstance(step, str):
                normalized.append({
                    "step": i + 1,
                    "skill": step,
                    "description": f"Develop proficiency in {step}",
                    "estimated_weeks": 4,
                })
            elif isinstance(step, dict):
                normalized.append({
                    "step": step.get("step", i + 1),
                    "skill": step.get("skill") or step.get("title") or f"Skill {i + 1}",
                    "description": step.get("description", ""),
                    "estimated_weeks": step.get("estimated_weeks", 4),
                })

        if not normalized and skill_gaps:
            return self._fallback_roadmap(skill_gaps)

        timeline = data.get("timeline", "")
        if isinstance(timeline, (int, float)):
            timeline = f"{int(timeline)} weeks estimated"
        elif not timeline:
            timeline = f"{len(skill_gaps) * 4} weeks estimated"

        return {
            "roadmap": normalized,
            "courses": data.get("courses", []),
            "certifications": data.get("certifications", []),
            "timeline": str(timeline),
        }

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

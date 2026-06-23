"""Resume parsing and AI analysis."""
import json
import re

from core.services import BaseService
from services.embedding import EmbeddingService
from utils.gemini_client import chat_completion_json, is_gemini_configured
from utils.pdf_parser import extract_text_from_pdf

_SKILL_KEYWORDS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby", "php",
    "react", "vue", "angular", "next.js", "nextjs", "django", "flask", "fastapi", "spring",
    "node.js", "nodejs", "express", "rest api", "graphql",
    "sql", "postgresql", "postgres", "mysql", "mongodb", "redis", "dynamodb",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ci/cd",
    "machine learning", "deep learning", "nlp", "llm", "rag", "generative ai",
    "prompt engineering", "agentic ai", "microservices", "git", "linux", "agile", "scrum",
    "pandas", "numpy", "tensorflow", "pytorch", "spark", "kafka", "selenium",
]


class ResumeAnalysisService(BaseService):
    def __init__(self):
        super().__init__()
        self.embedding_service = EmbeddingService()

    def extract_text_from_pdf(self, file_path: str) -> str:
        return extract_text_from_pdf(file_path)

    def parse_and_analyze(self, raw_text: str, user=None) -> tuple[dict, dict]:
        """Single Gemini call for structured parse + summary (falls back locally on error)."""
        if not is_gemini_configured():
            structured = self._fallback_parse(raw_text)
            return structured, self._fallback_analysis(structured, raw_text)

        prompt = f"""You are an expert resume parser and career advisor.

Analyze this resume and return JSON with:
- skills: list of all technical and soft skills (strings)
- education: list of objects with degree, institution, year
- work_experience: list of objects with title, company, description, start_date, end_date
- projects: list of objects with name, description, technologies
- certifications: list of strings
- summary: 2-3 sentence professional summary
- strengths: list of top 5 candidate strengths
- experience_level: one of junior, mid, senior, lead

Resume:
{raw_text[:8000]}"""

        try:
            result = chat_completion_json(
                [{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            structured = {
                "skills": result.get("skills", []),
                "education": result.get("education", []),
                "work_experience": result.get("work_experience", []),
                "projects": result.get("projects", []),
                "certifications": result.get("certifications", []),
            }
            analysis = {
                "summary": result.get("summary", ""),
                "strengths": result.get("strengths", []),
                "experience_level": result.get("experience_level", "mid"),
            }
            self.embedding_service.log_ai_call(
                user, "resume_analysis", "parse_and_analyze",
                {"skills_count": len(structured["skills"])},
                {**structured, **analysis},
            )
            return structured, analysis
        except Exception as e:
            self.logger.error("Resume parse/analyze failed: %s", e)
            structured = self._fallback_parse(raw_text)
            return structured, self._fallback_analysis(structured, raw_text)

    def process_resume(self, resume, user):
        """Full pipeline: extract text, persist it, then parse, analyze, embed."""
        file_path = resume.file.path
        raw_text = self.extract_text_from_pdf(file_path)

        if not raw_text.strip():
            self.logger.warning("No text extracted from resume %s", resume.id)

        resume.raw_text = raw_text
        resume.save(update_fields=["raw_text", "updated_at"])

        structured, analysis = self.parse_and_analyze(raw_text, user)

        resume.skills = structured.get("skills", [])
        resume.education = structured.get("education", [])
        resume.work_experience = structured.get("work_experience", [])
        resume.projects = structured.get("projects", [])
        resume.certifications = structured.get("certifications", [])
        resume.structured_data = structured
        resume.ai_summary = analysis.get("summary", "")
        resume.save()

        embed_text = f"{raw_text[:4000]} Skills: {', '.join(resume.skills)}"
        try:
            embedding = self.embedding_service.generate_embedding(embed_text)
            self.embedding_service.store_resume_embedding(resume.id, embedding, user)
        except Exception as e:
            self.logger.warning(
                "Resume saved but embedding skipped (Gemini quota/API): %s", e
            )
        return resume

    def reprocess_from_stored_text(self, resume, user):
        """Re-run AI analysis on already-extracted raw_text (no PDF re-read)."""
        if not resume.raw_text.strip():
            return self.process_resume(resume, user)

        structured, analysis = self.parse_and_analyze(resume.raw_text, user)
        resume.skills = structured.get("skills", [])
        resume.education = structured.get("education", [])
        resume.work_experience = structured.get("work_experience", [])
        resume.projects = structured.get("projects", [])
        resume.certifications = structured.get("certifications", [])
        resume.structured_data = structured
        resume.ai_summary = analysis.get("summary", "")
        resume.save()

        embed_text = f"{resume.raw_text[:4000]} Skills: {', '.join(resume.skills)}"
        try:
            embedding = self.embedding_service.generate_embedding(embed_text)
            self.embedding_service.store_resume_embedding(resume.id, embedding, user)
        except Exception as e:
            self.logger.warning("Reprocess embedding skipped: %s", e)
        return resume

    def _fallback_analysis(self, structured_data: dict, raw_text: str = "") -> dict:
        skills = structured_data.get("skills", [])
        summary = self._extract_summary_from_text(raw_text)
        if not summary:
            summary_skills = ", ".join(skills[:8]) if skills else "various technologies"
            summary = f"Professional with experience in {summary_skills}."
        return {
            "summary": summary,
            "strengths": skills[:5],
            "experience_level": "mid",
        }

    def _fallback_parse(self, raw_text: str) -> dict:
        text = raw_text.lower()
        found = []
        for skill in _SKILL_KEYWORDS:
            if skill in text and skill not in found:
                found.append(skill.title() if skill.isascii() else skill)
        return {
            "skills": found or ["Communication", "Problem-solving"],
            "education": [],
            "work_experience": [],
            "projects": [],
            "certifications": [],
        }

    @staticmethod
    def _extract_summary_from_text(raw_text: str) -> str:
        match = re.search(
            r"(?i)summary\s*\n+(.+?)(?:\n\s*(?:experience|education|skills|projects|"
            r"work experience|technical skills|certifications)\b)",
            raw_text,
            re.DOTALL,
        )
        if match:
            return " ".join(match.group(1).split())[:800]
        for line in raw_text.split("\n"):
            stripped = line.strip()
            if len(stripped) > 100:
                return stripped[:800]
        return ""

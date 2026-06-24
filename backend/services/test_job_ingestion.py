"""Job ingestion unit tests."""
from services.job_ingestion import (
    NormalizedJob,
    infer_experience_level,
    matches_search,
    strip_html,
)
from utils.skills import extract_skills_from_text


def _job(title: str, company: str = "Acme") -> NormalizedJob:
    return NormalizedJob(
        source="test",
        external_id="1",
        title=title,
        company=company,
        description="We need a developer for analytics dashboards.",
        location="Remote",
        is_remote=True,
        experience_level="mid",
        required_skills=[],
        salary_range="",
        employment_type="full-time",
        source_url="",
        posted_at=None,
    )


class TestJobIngestionHelpers:
    def test_strip_html(self):
        assert "Hello world" in strip_html("<p>Hello <b>world</b></p>")

    def test_infer_experience_level(self):
        assert infer_experience_level("Junior Software Engineer") == "junior"
        assert infer_experience_level("Senior Backend Engineer") == "senior"
        assert infer_experience_level("Software Engineer") == "mid"

    def test_extract_skills(self):
        skills = extract_skills_from_text("We need Python, Django, and PostgreSQL experience.")
        assert "Python" in skills
        assert "Django" in skills

    def test_matches_search_title_only(self):
        assert matches_search(_job("Senior Software Developer"), "developer")
        assert not matches_search(_job("Business Analyst"), "developer")
        assert not matches_search(_job("Data Analyst", company="Acme Corp"), "developer")

    def test_matches_search_all_tokens(self):
        assert matches_search(_job("Full Stack Developer"), "full developer")
        assert not matches_search(_job("Backend Developer"), "full developer")

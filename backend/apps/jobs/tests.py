import pytest
from django.contrib.auth import get_user_model

from apps.jobs.models import Job

User = get_user_model()


@pytest.mark.django_db
class TestJobModel:
    def test_create_job(self):
        job = Job.objects.create(
            title="Software Engineer",
            company="Test Co",
            description="A test job",
            required_skills=["Python", "Django"],
        )
        assert str(job) == "Software Engineer at Test Co"
        assert job.is_active is True

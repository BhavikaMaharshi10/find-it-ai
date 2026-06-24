"""Seed sample jobs and generate embeddings."""
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.jobs.models import Job
from services.embedding import EmbeddingService

SAMPLE_JOBS = [
    {
        "title": "Software Engineer",
        "company": "ABC Tech",
        "description": "Build scalable web applications using Python and React. Work with cross-functional teams.",
        "location": "San Francisco, CA",
        "is_remote": True,
        "experience_level": "mid",
        "required_skills": ["Python", "React", "PostgreSQL", "Docker"],
        "preferred_skills": ["AWS", "TypeScript"],
        "salary_range": "$120,000 - $160,000",
    },
    {
        "title": "Senior Full Stack Developer",
        "company": "InnovateCo",
        "description": "Lead development of AI-powered SaaS products. Mentor junior developers.",
        "location": "New York, NY",
        "is_remote": False,
        "experience_level": "senior",
        "required_skills": ["Python", "Django", "React", "PostgreSQL", "AWS"],
        "preferred_skills": ["OpenAI", "Docker", "Kubernetes"],
        "salary_range": "$150,000 - $190,000",
    },
    {
        "title": "Frontend Engineer",
        "company": "DesignFirst",
        "description": "Create beautiful, responsive user interfaces with React and TypeScript.",
        "location": "Remote",
        "is_remote": True,
        "experience_level": "mid",
        "required_skills": ["React", "TypeScript", "CSS", "JavaScript"],
        "preferred_skills": ["Framer Motion", "Next.js"],
        "salary_range": "$100,000 - $140,000",
    },
    {
        "title": "ML Engineer",
        "company": "DataMind AI",
        "description": "Build and deploy machine learning models for recommendation systems.",
        "location": "Seattle, WA",
        "is_remote": True,
        "experience_level": "senior",
        "required_skills": ["Python", "PyTorch", "ML", "NLP", "Docker"],
        "preferred_skills": ["OpenAI", "RAG", "pgvector"],
        "salary_range": "$160,000 - $200,000",
    },
    {
        "title": "Junior Backend Developer",
        "company": "StartupHub",
        "description": "Entry-level backend role working with Django REST APIs.",
        "location": "Austin, TX",
        "is_remote": True,
        "experience_level": "junior",
        "required_skills": ["Python", "Django", "SQL", "Git"],
        "preferred_skills": ["REST APIs", "PostgreSQL"],
        "salary_range": "$70,000 - $90,000",
    },
    {
        "title": "DevOps Engineer",
        "company": "CloudScale",
        "description": "Manage CI/CD pipelines and cloud infrastructure on AWS.",
        "location": "Denver, CO",
        "is_remote": True,
        "experience_level": "mid",
        "required_skills": ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux"],
        "preferred_skills": ["Terraform", "Python"],
        "salary_range": "$130,000 - $170,000",
    },
    {
        "title": "AI Product Engineer",
        "company": "FindIt Labs",
        "description": "Build AI-powered features using LLMs, RAG, and vector databases.",
        "location": "Remote",
        "is_remote": True,
        "experience_level": "senior",
        "required_skills": ["Python", "OpenAI", "RAG", "PostgreSQL", "React"],
        "preferred_skills": ["pgvector", "Django", "TypeScript"],
        "salary_range": "$170,000 - $210,000",
    },
    {
        "title": "Data Engineer",
        "company": "AnalyticsPro",
        "description": "Design data pipelines and ETL processes for large-scale analytics.",
        "location": "Chicago, IL",
        "is_remote": False,
        "experience_level": "mid",
        "required_skills": ["Python", "SQL", "ETL", "Spark", "AWS"],
        "preferred_skills": ["Airflow", "dbt"],
        "salary_range": "$125,000 - $155,000",
    },
]


class Command(BaseCommand):
    help = "Seed sample jobs and generate embeddings"

    def handle(self, *args, **options):
        embedding_service = EmbeddingService()
        created_count = 0

        for job_data in SAMPLE_JOBS:
            job, created = Job.objects.get_or_create(
                title=job_data["title"],
                company=job_data["company"],
                source="seed",
                defaults={**job_data, "source": "seed", "posted_at": timezone.now()},
            )
            if created:
                created_count += 1

            embed_text = (
                f"{job.title} at {job.company}. {job.description} "
                f"Skills: {', '.join(job.required_skills)}"
            )
            try:
                embedding = embedding_service.generate_embedding(embed_text)
                embedding_service.store_job_embedding(job.id, embedding)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Embedding skipped for {job.title}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} new jobs ({len(SAMPLE_JOBS)} total)."))

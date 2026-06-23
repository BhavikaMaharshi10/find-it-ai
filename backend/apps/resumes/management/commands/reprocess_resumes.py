from django.core.management.base import BaseCommand

from apps.resumes.models import Resume
from services.resume_analysis import ResumeAnalysisService


class Command(BaseCommand):
    help = "Re-run AI analysis on uploaded resumes (uses stored raw_text)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--active-only",
            action="store_true",
            help="Only reprocess active resumes",
        )

    def handle(self, *args, **options):
        qs = Resume.objects.select_related("user")
        if options["active_only"]:
            qs = qs.filter(is_active=True)

        service = ResumeAnalysisService()
        count = 0
        for resume in qs:
            self.stdout.write(f"Reprocessing {resume.original_filename} ({resume.user.email})...")
            service.reprocess_from_stored_text(resume, resume.user)
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Reprocessed {count} resume(s)."))

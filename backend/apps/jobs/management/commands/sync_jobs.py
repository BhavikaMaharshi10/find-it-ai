"""Sync live job postings from free public APIs."""
from django.core.management.base import BaseCommand

from services.job_ingestion import JobIngestionService


class Command(BaseCommand):
    help = "Sync live jobs from Remotive, Lever, and Greenhouse (free, no API keys)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--greenhouse-limit",
            type=int,
            default=12,
            help="Max jobs per Greenhouse board (default: 12)",
        )
        parser.add_argument(
            "--lever-limit",
            type=int,
            default=20,
            help="Max jobs per Lever company (default: 20)",
        )
        parser.add_argument(
            "--remotive-limit",
            type=int,
            default=50,
            help="Max jobs from Remotive (default: 50)",
        )
        parser.add_argument(
            "--skip-embeddings",
            action="store_true",
            help="Skip Gemini embeddings (use if API quota is exhausted)",
        )
        parser.add_argument(
            "--keep-stale",
            action="store_true",
            help="Do not deactivate jobs missing from the latest sync",
        )

    def handle(self, *args, **options):
        service = JobIngestionService()
        result = service.sync_all(
            greenhouse_limit=options["greenhouse_limit"],
            lever_limit=options["lever_limit"],
            remotive_limit=options["remotive_limit"],
            embed=not options["skip_embeddings"],
            deactivate_missing=not options["keep_stale"],
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {result['unique']} live jobs "
                f"({result['created']} new, {result['updated']} updated, "
                f"{result['embedded']} embedded, {result['deactivated']} deactivated)"
            )
        )

        if result["errors"]:
            self.stdout.write(self.style.WARNING(f"{len(result['errors'])} warning(s):"))
            for err in result["errors"][:10]:
                self.stdout.write(f"  - {err}")
            if len(result["errors"]) > 10:
                self.stdout.write(f"  ... and {len(result['errors']) - 10} more")

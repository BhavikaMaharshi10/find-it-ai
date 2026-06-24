"""Ingest live job postings from free public APIs (no API keys)."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
from html import unescape

import urllib.error

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.jobs.models import Job
from core.services import BaseService
from services.embedding import EmbeddingService
from utils.http_client import fetch_json
from utils.skills import extract_skills_from_text

# Public Greenhouse boards (no auth): boards-api.greenhouse.io/v1/boards/{token}/jobs
GREENHOUSE_BOARDS: dict[str, str] = {
    "stripe": "Stripe",
    "airbnb": "Airbnb",
    "discord": "Discord",
    "figma": "Figma",
    "datadog": "Datadog",
    "cloudflare": "Cloudflare",
    "gitlab": "GitLab",
    "mongodb": "MongoDB",
    "asana": "Asana",
    "robinhood": "Robinhood",
}

# Public Lever boards: api.lever.co/v0/postings/{company}?mode=json
LEVER_COMPANIES: dict[str, str] = {
    "spotify": "Spotify",
    "palantir": "Palantir",
    "netflix": "Netflix",
    "atlassian": "Atlassian",
}

REMOTIVE_API = "https://remotive.com/api/remote-jobs"
LIVE_CACHE_TTL_SECONDS = 600  # 10 minutes


def resolve_job_identity(
    *,
    source: str = "",
    external_id: str = "",
    source_url: str = "",
    external_key: str = "",
) -> tuple[str, str]:
    """Return a stable (source, external_id) pair for upserts."""
    if external_key and ":" in external_key:
        key_source, key_id = external_key.split(":", 1)
        if key_source and key_id:
            return key_source, key_id

    resolved_source = (source or "live").strip() or "live"
    resolved_id = str(external_id or "").strip()
    if not resolved_id and source_url:
        resolved_id = hashlib.sha256(source_url.encode()).hexdigest()[:32]
    if not resolved_id:
        raise ValueError("Job identity requires external_id, external_key, or source_url.")

    return resolved_source, resolved_id


def matches_search(job: NormalizedJob, query: str) -> bool:
    """All search terms must appear in the job title or company (not description)."""
    tokens = [t.lower() for t in query.split() if t.strip()]
    if not tokens:
        return True
    title = job.title.lower()
    company = job.company.lower()
    haystack = f"{title} {company}"
    return all(token in haystack for token in tokens)


def matches_filters(
    job: NormalizedJob,
    *,
    is_remote: bool | None,
    experience_level: str | None,
) -> bool:
    if is_remote is not None and job.is_remote != is_remote:
        return False
    if experience_level and job.experience_level != experience_level:
        return False
    return True


def normalized_to_dict(item: NormalizedJob) -> dict:
    return {
        "external_key": f"{item.source}:{item.external_id}",
        "source": item.source,
        "external_id": item.external_id,
        "title": item.title,
        "company": item.company,
        "description": item.description,
        "location": item.location,
        "is_remote": item.is_remote,
        "experience_level": item.experience_level,
        "required_skills": item.required_skills,
        "preferred_skills": [],
        "salary_range": item.salary_range,
        "employment_type": item.employment_type,
        "source_url": item.source_url,
        "posted_at": item.posted_at.isoformat() if item.posted_at else None,
    }


def dict_to_normalized(data: dict) -> NormalizedJob:
    posted = data.get("posted_at")
    posted_at = parse_posted_at(posted) if posted else None
    source, external_id = resolve_job_identity(
        source=str(data.get("source", "")),
        external_id=str(data.get("external_id", "")),
        source_url=str(data.get("source_url", "")),
        external_key=str(data.get("external_key", "")),
    )
    return NormalizedJob(
        source=source,
        external_id=external_id,
        title=data["title"],
        company=data["company"],
        description=data.get("description", data["title"]),
        location=data.get("location", ""),
        is_remote=bool(data.get("is_remote", False)),
        experience_level=data.get("experience_level", "mid"),
        required_skills=list(data.get("required_skills") or []),
        salary_range=data.get("salary_range", "") or "",
        employment_type=data.get("employment_type", "full-time") or "full-time",
        source_url=data.get("source_url", "") or "",
        posted_at=posted_at,
    )


@dataclass
class NormalizedJob:
    source: str
    external_id: str
    title: str
    company: str
    description: str
    location: str
    is_remote: bool
    experience_level: str
    required_skills: list[str]
    salary_range: str
    employment_type: str
    source_url: str
    posted_at: datetime | None


def strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    return unescape(re.sub(r"\s+", " ", text)).strip()


def infer_experience_level(title: str) -> str:
    title_lower = title.lower()
    if any(k in title_lower for k in ("intern", "internship", "entry", "junior", "graduate", "new grad")):
        return "junior"
    if any(k in title_lower for k in ("staff", "principal", "distinguished", "lead", "director", "head of")):
        return "lead"
    if "senior" in title_lower or "sr." in title_lower or "sr " in title_lower:
        return "senior"
    return "mid"


def parse_posted_at(value: str | int | float | None) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        # Lever uses millisecond timestamps
        seconds = value / 1000 if value > 1_000_000_000_000 else value
        return datetime.fromtimestamp(seconds, tz=dt_timezone.utc)
    parsed = parse_datetime(str(value))
    if parsed is None:
        return None
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone=dt_timezone.utc)
    return parsed


class JobIngestionService(BaseService):
    _live_cache: list[NormalizedJob] | None = None
    _live_cache_at: float = 0.0

    def __init__(self):
        super().__init__()
        self.embedding_service = EmbeddingService()

    def search_live(
        self,
        *,
        search: str = "",
        is_remote: bool | None = None,
        experience_level: str | None = None,
        refresh: bool = False,
    ) -> dict:
        """Fetch jobs from live APIs, filter in memory, do not write to DB."""
        import time

        jobs = self._get_live_pool(refresh=refresh)
        filtered = [
            j
            for j in jobs
            if matches_search(j, search) and matches_filters(
                j, is_remote=is_remote, experience_level=experience_level
            )
        ]
        filtered.sort(
            key=lambda j: j.posted_at or datetime.min.replace(tzinfo=dt_timezone.utc),
            reverse=True,
        )
        return {
            "count": len(filtered),
            "results": [normalized_to_dict(j) for j in filtered],
            "cached": not refresh and (time.time() - self._live_cache_at) < LIVE_CACHE_TTL_SECONDS,
        }

    def persist_job(self, data: dict) -> Job:
        """Save a live job to the DB only when the user saves or applies."""
        item = dict_to_normalized(data)
        job, _ = self._upsert_job(item)
        return job

    def _get_live_pool(self, refresh: bool = False) -> list[NormalizedJob]:
        import time

        now = time.time()
        if (
            not refresh
            and JobIngestionService._live_cache is not None
            and (now - JobIngestionService._live_cache_at) < LIVE_CACHE_TTL_SECONDS
        ):
            return JobIngestionService._live_cache

        errors: list[str] = []
        jobs: list[NormalizedJob] = []

        from concurrent.futures import ThreadPoolExecutor, as_completed

        fetchers = (
            lambda: self._fetch_remotive(50, errors),
            lambda: self._fetch_lever(30, errors),
            lambda: self._fetch_greenhouse(15, errors, fetch_details=False),
        )
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(fn) for fn in fetchers]
            for future in as_completed(futures):
                try:
                    jobs.extend(future.result())
                except Exception as exc:
                    errors.append(str(exc))

        seen: set[tuple[str, str]] = set()
        unique: list[NormalizedJob] = []
        for job in jobs:
            key = (job.source, job.external_id)
            if key not in seen:
                seen.add(key)
                unique.append(job)

        JobIngestionService._live_cache = unique
        JobIngestionService._live_cache_at = now
        if errors:
            self.logger.warning("Live fetch warnings: %s", errors[:5])
        return unique

    def sync_all(
        self,
        *,
        greenhouse_limit: int = 12,
        lever_limit: int = 20,
        remotive_limit: int = 50,
        embed: bool = True,
        deactivate_missing: bool = True,
    ) -> dict:
        normalized: list[NormalizedJob] = []
        errors: list[str] = []

        normalized.extend(self._fetch_remotive(remotive_limit, errors))
        normalized.extend(self._fetch_lever(lever_limit, errors))
        normalized.extend(self._fetch_greenhouse(greenhouse_limit, errors, fetch_details=True))

        seen_keys: set[tuple[str, str]] = set()
        created = updated = embedded = 0

        for item in normalized:
            key = (item.source, item.external_id)
            if key in seen_keys:
                continue
            seen_keys.add(key)

            job, was_created = self._upsert_job(item)
            if was_created:
                created += 1
            else:
                updated += 1

            if embed:
                try:
                    self._embed_job(job)
                    embedded += 1
                except Exception as e:
                    errors.append(f"Embedding failed for {job.title}: {e}")

        deactivated = 0
        if deactivate_missing and seen_keys:
            for source in {src for src, _ in seen_keys}:
                external_ids = [ext for src, ext in seen_keys if src == source]
                deactivated += (
                    Job.objects.filter(source=source, is_active=True)
                    .exclude(external_id__in=external_ids)
                    .update(is_active=False)
                )

        return {
            "fetched": len(normalized),
            "unique": len(seen_keys),
            "created": created,
            "updated": updated,
            "embedded": embedded,
            "deactivated": deactivated,
            "errors": errors,
        }

    def _upsert_job(self, item: NormalizedJob) -> tuple[Job, bool]:
        source, external_id = resolve_job_identity(
            source=item.source,
            external_id=item.external_id,
            source_url=item.source_url,
        )
        defaults = {
            "title": item.title[:255],
            "company": item.company[:255],
            "description": item.description,
            "location": item.location[:255],
            "is_remote": item.is_remote,
            "experience_level": item.experience_level,
            "required_skills": item.required_skills,
            "preferred_skills": [],
            "salary_range": item.salary_range[:100],
            "employment_type": item.employment_type[:50],
            "source_url": item.source_url,
            "posted_at": item.posted_at,
            "is_active": True,
        }
        job, created = Job.objects.update_or_create(
            source=source,
            external_id=external_id,
            defaults=defaults,
        )
        return job, created

    def _embed_job(self, job: Job) -> None:
        embed_text = (
            f"{job.title} at {job.company}. {job.description[:4000]} "
            f"Skills: {', '.join(job.required_skills or [])}"
        )
        embedding = self.embedding_service.generate_embedding(embed_text)
        self.embedding_service.store_job_embedding(job.id, embedding)

    def _fetch_remotive(self, limit: int, errors: list[str]) -> list[NormalizedJob]:
        results: list[NormalizedJob] = []
        try:
            data = fetch_json(REMOTIVE_API)
            for row in (data.get("jobs") or [])[:limit]:
                description = strip_html(row.get("description", ""))
                title = row.get("title", "").strip()
                if not title:
                    continue
                company = row.get("company_name", "Unknown").strip()
                results.append(
                    NormalizedJob(
                        source="remotive",
                        external_id=str(row.get("id", "")),
                        title=title,
                        company=company,
                        description=description or title,
                        location=row.get("candidate_required_location", "Remote") or "Remote",
                        is_remote=True,
                        experience_level=infer_experience_level(title),
                        required_skills=extract_skills_from_text(description + " " + title),
                        salary_range=row.get("salary", "") or "",
                        employment_type=(row.get("job_type") or "full-time").lower(),
                        source_url=row.get("url", "") or "",
                        posted_at=parse_posted_at(row.get("publication_date")),
                    )
                )
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
            errors.append(f"Remotive: {e}")
        return results

    def _fetch_lever(self, per_company: int, errors: list[str]) -> list[NormalizedJob]:
        results: list[NormalizedJob] = []
        for slug, company_name in LEVER_COMPANIES.items():
            try:
                url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
                postings = fetch_json(url)
                for row in (postings or [])[:per_company]:
                    title = row.get("text", "").strip()
                    if not title:
                        continue
                    description = row.get("descriptionPlain", "") or title
                    categories = row.get("categories", {}) or {}
                    location = categories.get("location", "") or ""
                    commitment = (categories.get("commitment") or "full-time").lower()
                    results.append(
                        NormalizedJob(
                            source="lever",
                            external_id=str(row.get("id", "")),
                            title=title,
                            company=company_name,
                            description=description,
                            location=location,
                            is_remote="remote" in location.lower() or not location,
                            experience_level=infer_experience_level(title),
                            required_skills=extract_skills_from_text(description),
                            salary_range="",
                            employment_type=commitment,
                            source_url=row.get("hostedUrl", "") or "",
                            posted_at=parse_posted_at(row.get("createdAt")),
                        )
                    )
            except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
                errors.append(f"Lever/{slug}: {e}")
        return results

    def _fetch_greenhouse(
        self, per_board: int, errors: list[str], *, fetch_details: bool = True
    ) -> list[NormalizedJob]:
        results: list[NormalizedJob] = []
        for board, company_name in GREENHOUSE_BOARDS.items():
            try:
                list_url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"
                payload = fetch_json(list_url)
                for summary in (payload.get("jobs") or [])[:per_board]:
                    job_id = summary.get("id")
                    title = summary.get("title", "").strip()
                    if not job_id or not title:
                        continue

                    location_obj = summary.get("location") or {}
                    location = (
                        location_obj.get("name", "")
                        if isinstance(location_obj, dict)
                        else str(location_obj)
                    )
                    source_url = summary.get("absolute_url", "") or ""

                    if fetch_details:
                        detail_url = (
                            f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{job_id}"
                        )
                        detail = fetch_json(detail_url)
                        description = strip_html(detail.get("content", "")) or title
                        location_obj = detail.get("location") or location_obj
                        location = (
                            location_obj.get("name", "")
                            if isinstance(location_obj, dict)
                            else str(location_obj)
                        )
                        source_url = detail.get("absolute_url", "") or source_url
                        posted_at = parse_posted_at(
                            detail.get("updated_at") or summary.get("updated_at")
                        )
                    else:
                        description = title
                        posted_at = parse_posted_at(summary.get("updated_at"))

                    results.append(
                        NormalizedJob(
                            source="greenhouse",
                            external_id=f"{board}:{job_id}",
                            title=title,
                            company=company_name,
                            description=description,
                            location=location,
                            is_remote="remote" in location.lower(),
                            experience_level=infer_experience_level(title),
                            required_skills=extract_skills_from_text(
                                description + " " + title
                            ),
                            salary_range="",
                            employment_type="full-time",
                            source_url=source_url,
                            posted_at=posted_at,
                        )
                    )
            except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
                errors.append(f"Greenhouse/{board}: {e}")
        return results

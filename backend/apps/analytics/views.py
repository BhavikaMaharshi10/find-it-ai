from collections import Counter
from datetime import timedelta

from django.db.models import Avg, Count
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.applications.models import Application
from apps.jobs.models import Job, SavedJob
from apps.recommendations.models import Recommendation


class DashboardStatsView(APIView):
    def get(self, request):
        user = request.user
        recommendations = Recommendation.objects.filter(user=user)
        applications = Application.objects.filter(user=user)

        return Response({
            "jobs_found": Job.objects.filter(is_active=True).count(),
            "saved_jobs": SavedJob.objects.filter(user=user).count(),
            "applications_sent": applications.count(),
            "average_match_score": round(
                recommendations.aggregate(avg=Avg("match_score"))["avg"] or 0, 1
            ),
        })


class MatchScoreDistributionView(APIView):
    def get(self, request):
        recs = Recommendation.objects.filter(user=request.user)
        buckets = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "below-60": 0}
        for rec in recs:
            score = rec.match_score
            if score >= 90:
                buckets["90-100"] += 1
            elif score >= 80:
                buckets["80-89"] += 1
            elif score >= 70:
                buckets["70-79"] += 1
            elif score >= 60:
                buckets["60-69"] += 1
            else:
                buckets["below-60"] += 1
        return Response(buckets)


class SkillGapAnalysisView(APIView):
    def get(self, request):
        recs = Recommendation.objects.filter(user=request.user)
        all_gaps = []
        for rec in recs:
            all_gaps.extend(rec.missing_skills or [])
        counter = Counter(all_gaps)
        top_gaps = [{"skill": k, "count": v} for k, v in counter.most_common(10)]
        return Response(top_gaps)


class ApplicationTrendsView(APIView):
    def get(self, request):
        user = request.user
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        apps = (
            Application.objects.filter(user=user, applied_date__gte=thirty_days_ago)
            .values("applied_date")
            .annotate(count=Count("id"))
            .order_by("applied_date")
        )
        return Response(list(apps))


class ApplicationStatusBreakdownView(APIView):
    def get(self, request):
        breakdown = (
            Application.objects.filter(user=request.user)
            .values("status")
            .annotate(count=Count("id"))
        )
        return Response(list(breakdown))

from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("stats/", views.DashboardStatsView.as_view(), name="dashboard-stats"),
    path("match-distribution/", views.MatchScoreDistributionView.as_view(), name="match-distribution"),
    path("skill-gaps/", views.SkillGapAnalysisView.as_view(), name="skill-gaps"),
    path("application-trends/", views.ApplicationTrendsView.as_view(), name="application-trends"),
    path("application-status/", views.ApplicationStatusBreakdownView.as_view(), name="application-status"),
]

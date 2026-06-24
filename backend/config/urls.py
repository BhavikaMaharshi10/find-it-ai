"""FindItAI URL configuration."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from core.views import HealthCheckView

urlpatterns = [
    path("api/v1/health/", HealthCheckView.as_view(), name="health-check"),
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/profile/", include("apps.profiles.urls")),
    path("api/v1/resume/", include("apps.resumes.urls")),
    path("api/v1/jobs/", include("apps.jobs.urls")),
    path("api/v1/recommendations/", include("apps.recommendations.urls")),
    path("api/v1/applications/", include("apps.applications.urls")),
    path("api/v1/dashboard/", include("apps.analytics.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

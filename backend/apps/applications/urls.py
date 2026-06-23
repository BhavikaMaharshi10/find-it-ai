from django.urls import path

from . import views

app_name = "applications"

urlpatterns = [
    path("", views.ApplicationListCreateView.as_view(), name="application-list"),
    path("<uuid:pk>/", views.ApplicationDetailView.as_view(), name="application-detail"),
]

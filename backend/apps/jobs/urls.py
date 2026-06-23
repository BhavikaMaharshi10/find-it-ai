from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("", views.JobListView.as_view(), name="job-list"),
    path("saved/", views.SavedJobListCreateView.as_view(), name="saved-job-list"),
    path("saved/<uuid:pk>/", views.SavedJobDetailView.as_view(), name="saved-job-detail"),
    path("saved/<uuid:pk>/notes/", views.SavedJobNotesView.as_view(), name="saved-job-notes"),
    path("<uuid:pk>/", views.JobDetailView.as_view(), name="job-detail"),
]

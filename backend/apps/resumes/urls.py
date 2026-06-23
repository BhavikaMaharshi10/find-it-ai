from django.urls import path

from . import views

app_name = "resumes"

urlpatterns = [
    path("", views.ResumeListView.as_view(), name="resume-list"),
    path("upload/", views.ResumeUploadView.as_view(), name="resume-upload"),
    path("active/", views.ResumeActiveView.as_view(), name="resume-active"),
    path("<uuid:pk>/", views.ResumeDetailView.as_view(), name="resume-detail"),
]

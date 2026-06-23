from django.urls import path

from . import views

app_name = "recommendations"

urlpatterns = [
    path("", views.RecommendationListView.as_view(), name="recommendation-list"),
    path("learning/", views.LearningRoadmapView.as_view(), name="learning-roadmap"),
    path("rag/", views.RAGQueryView.as_view(), name="rag-query"),
    path("<uuid:pk>/", views.RecommendationDetailView.as_view(), name="recommendation-detail"),
]

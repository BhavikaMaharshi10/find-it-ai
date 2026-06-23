from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.resumes.models import Resume
from rag.pipeline import RAGService
from services.learning import LearningRecommendationService
from services.recommendation import RecommendationService

from .models import Recommendation
from .serializers import RecommendationDetailSerializer, RecommendationSerializer


class RecommendationListView(APIView):
    def get(self, request):
        service = RecommendationService()
        top_k = int(request.query_params.get("top_k", 10))
        results = service.find_similar_jobs(request.user, top_k=top_k)
        stored = Recommendation.objects.filter(user=request.user).select_related("job")[:top_k]
        return Response(RecommendationSerializer(stored, many=True).data)

    def post(self, request):
        """Trigger fresh recommendation generation."""
        service = RecommendationService()
        top_k = int(request.data.get("top_k", 10))
        service.find_similar_jobs(request.user, top_k=top_k)
        stored = Recommendation.objects.filter(user=request.user).select_related("job")[:top_k]
        return Response(RecommendationSerializer(stored, many=True).data)


class RecommendationDetailView(APIView):
    def get(self, request, pk):
        try:
            rec = Recommendation.objects.select_related("job").prefetch_related(
                "skill_gaps"
            ).get(pk=pk, user=request.user)
        except Recommendation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        rec.is_viewed = True
        rec.save(update_fields=["is_viewed"])
        return Response(RecommendationDetailSerializer(rec).data)


class LearningRoadmapView(APIView):
    def get(self, request):
        resume = Resume.objects.filter(user=request.user, is_active=True).first()
        skill_gaps = request.query_params.get("skills", "").split(",")
        if not skill_gaps or skill_gaps == [""]:
            rec = Recommendation.objects.filter(user=request.user).first()
            skill_gaps = rec.missing_skills if rec else []

        service = LearningRecommendationService()
        roadmap = service.generate_learning_roadmap(
            skill_gaps,
            {
                "skills": resume.skills if resume else [],
                "summary": resume.ai_summary if resume else "",
            },
        )
        return Response(roadmap)


class RAGQueryView(APIView):
    def post(self, request):
        query = request.data.get("query", "Find me matching jobs")
        service = RAGService()
        result = service.run_pipeline(request.user, query)
        return Response(result)

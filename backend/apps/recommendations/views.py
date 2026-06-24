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
        # Recommendations are generated on demand from live job APIs.
        return Response([])

    def post(self, request):
        """Generate matches from live job postings."""
        service = RecommendationService()
        top_k = int(request.data.get("top_k", 10))
        refresh = request.data.get("refresh", False) in (True, "true", "1", 1)
        results = service.find_live_matches(request.user, top_k=top_k, refresh=refresh)
        return Response(results)


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
        skills_param = request.query_params.get("skills", "").strip()
        if skills_param:
            skill_gaps = [s.strip() for s in skills_param.split(",") if s.strip()]
        else:
            skill_gaps = []
            seen = set()
            for rec in Recommendation.objects.filter(user=request.user):
                for skill in rec.missing_skills or []:
                    key = skill.lower().strip()
                    if key and key not in seen:
                        seen.add(key)
                        skill_gaps.append(skill)

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

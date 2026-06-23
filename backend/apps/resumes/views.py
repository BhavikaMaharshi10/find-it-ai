from rest_framework import generics, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from services.resume_analysis import ResumeAnalysisService

from .models import Resume
from .serializers import ResumeSerializer, ResumeUploadSerializer


class ResumeListView(generics.ListAPIView):
    serializer_class = ResumeSerializer

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)


class ResumeUploadView(generics.CreateAPIView):
    serializer_class = ResumeUploadSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resume = serializer.save()
        service = ResumeAnalysisService()
        service.process_resume(resume, request.user)
        resume.refresh_from_db()
        return Response(
            ResumeSerializer(resume).data,
            status=status.HTTP_201_CREATED,
        )


class ResumeDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ResumeSerializer

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)


class ResumeActiveView(APIView):
    def get(self, request):
        resume = Resume.objects.filter(user=request.user, is_active=True).first()
        if not resume:
            return Response({"detail": "No active resume found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ResumeSerializer(resume).data)

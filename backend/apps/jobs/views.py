from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Job, SavedJob
from .serializers import JobFilter, JobSerializer, SavedJobSerializer


class JobListView(generics.ListAPIView):
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = JobFilter
    search_fields = ["title", "company", "description", "location"]
    ordering_fields = ["posted_at", "created_at", "title", "company"]
    ordering = ["-posted_at"]

    def get_queryset(self):
        return Job.objects.filter(is_active=True)


class JobDetailView(generics.RetrieveAPIView):
    serializer_class = JobSerializer
    queryset = Job.objects.filter(is_active=True)


class SavedJobListCreateView(generics.ListCreateAPIView):
    serializer_class = SavedJobSerializer

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related("job")

    def create(self, request, *args, **kwargs):
        job_id = request.data.get("job_id")
        saved, created = SavedJob.objects.get_or_create(
            user=request.user,
            job_id=job_id,
            defaults={"notes": request.data.get("notes", "")},
        )
        if not created and request.data.get("notes"):
            saved.notes = request.data["notes"]
            saved.save()
        return Response(
            SavedJobSerializer(saved).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class SavedJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SavedJobSerializer

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)


class SavedJobNotesView(APIView):
    def patch(self, request, pk):
        try:
            saved = SavedJob.objects.get(pk=pk, user=request.user)
        except SavedJob.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        saved.notes = request.data.get("notes", saved.notes)
        saved.save()
        return Response(SavedJobSerializer(saved).data)

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from services.job_ingestion import JobIngestionService

from .models import Job, SavedJob
from .serializers import JobSerializer, LiveJobSearchSerializer, SavedJobSerializer


class JobLiveSearchView(APIView):
    """Search live job postings from external APIs (not stored in DB)."""

    def get(self, request):
        search = request.query_params.get("search", "").strip()
        is_remote_param = request.query_params.get("is_remote", "")
        experience = request.query_params.get("experience_level", "").strip() or None
        refresh = request.query_params.get("refresh", "").lower() in ("1", "true", "yes")

        is_remote = None
        if is_remote_param.lower() == "true":
            is_remote = True
        elif is_remote_param.lower() == "false":
            is_remote = False

        service = JobIngestionService()
        payload = service.search_live(
            search=search,
            is_remote=is_remote,
            experience_level=experience,
            refresh=refresh,
        )
        return Response(payload)


class JobDetailView(generics.RetrieveAPIView):
    serializer_class = JobSerializer
    queryset = Job.objects.filter(is_active=True)


class SavedJobListCreateView(generics.ListCreateAPIView):
    serializer_class = SavedJobSerializer

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user).select_related("job")

    def create(self, request, *args, **kwargs):
        job_payload = request.data.get("job")
        job_id = request.data.get("job_id")

        if job_payload and not job_id:
            job = JobIngestionService().persist_job(job_payload)
            job_id = str(job.id)

        if not job_id:
            return Response(
                {"detail": "job_id or job payload is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

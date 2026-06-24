from rest_framework import serializers

from apps.jobs.serializers import JobSerializer
from services.job_ingestion import JobIngestionService

from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    job_id = serializers.UUIDField(write_only=True, required=False)
    job_payload = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = Application
        fields = (
            "id",
            "job",
            "job_id",
            "job_payload",
            "status",
            "notes",
            "applied_date",
            "interview_date",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "applied_date", "created_at", "updated_at")

    def create(self, validated_data):
        job_payload = validated_data.pop("job_payload", None)
        job_id = validated_data.pop("job_id", None)

        if job_payload and not job_id:
            job = JobIngestionService().persist_job(job_payload)
            job_id = job.id

        if not job_id:
            raise serializers.ValidationError("job_id or job_payload is required.")

        user = validated_data.pop("user", None) or self.context["request"].user
        application, created = Application.objects.get_or_create(
            user=user,
            job_id=job_id,
            defaults=validated_data,
        )
        if not created:
            # Re-marking the same job should not wipe an advanced pipeline status.
            validated_data.pop("status", None)
            if validated_data:
                for field, value in validated_data.items():
                    setattr(application, field, value)
                application.save(update_fields=[*validated_data.keys(), "updated_at"])
        return application

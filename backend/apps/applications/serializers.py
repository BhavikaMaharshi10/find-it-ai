from rest_framework import serializers

from apps.jobs.serializers import JobSerializer

from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    job_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Application
        fields = (
            "id",
            "job",
            "job_id",
            "status",
            "notes",
            "applied_date",
            "interview_date",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "applied_date", "created_at", "updated_at")

    def create(self, validated_data):
        job_id = validated_data.pop("job_id", None)
        if job_id:
            validated_data["job_id"] = job_id
        return Application.objects.create(
            user=self.context["request"].user,
            **validated_data,
        )

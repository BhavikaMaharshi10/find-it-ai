import django_filters
from rest_framework import serializers

from .models import Job, SavedJob


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "title",
            "company",
            "description",
            "location",
            "is_remote",
            "experience_level",
            "required_skills",
            "preferred_skills",
            "salary_range",
            "employment_type",
            "source_url",
            "posted_at",
            "created_at",
        )


class SavedJobSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    job_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = SavedJob
        fields = ("id", "job", "job_id", "notes", "saved_at")
        read_only_fields = ("id", "saved_at")

    def create(self, validated_data):
        job_id = validated_data.pop("job_id")
        return SavedJob.objects.get_or_create(
            user=self.context["request"].user,
            job_id=job_id,
            defaults={"notes": validated_data.get("notes", "")},
        )[0]


class JobFilter(django_filters.FilterSet):
    is_remote = django_filters.BooleanFilter()
    experience_level = django_filters.CharFilter()
    location = django_filters.CharFilter(lookup_expr="icontains")
    skill = django_filters.CharFilter(method="filter_skill")

    class Meta:
        model = Job
        fields = ["is_remote", "experience_level", "location"]

    def filter_skill(self, queryset, name, value):
        return queryset.filter(required_skills__icontains=value)

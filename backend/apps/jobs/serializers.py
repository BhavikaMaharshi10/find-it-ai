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
            "source",
            "external_id",
            "source_url",
            "posted_at",
            "created_at",
        )


class LiveJobSearchSerializer(serializers.Serializer):
    external_key = serializers.CharField()
    source = serializers.CharField()
    external_id = serializers.CharField()
    title = serializers.CharField()
    company = serializers.CharField()
    description = serializers.CharField()
    location = serializers.CharField()
    is_remote = serializers.BooleanField()
    experience_level = serializers.CharField()
    required_skills = serializers.ListField(child=serializers.CharField())
    salary_range = serializers.CharField()
    employment_type = serializers.CharField()
    source_url = serializers.URLField(allow_blank=True)
    posted_at = serializers.DateTimeField(allow_null=True)


class SavedJobSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    job_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = SavedJob
        fields = ("id", "job", "job_id", "notes", "saved_at")
        read_only_fields = ("id", "saved_at")


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

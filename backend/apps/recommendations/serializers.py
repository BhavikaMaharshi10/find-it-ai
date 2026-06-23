from rest_framework import serializers

from apps.jobs.serializers import JobSerializer

from .models import Recommendation, SkillGap


class SkillGapSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillGap
        fields = ("id", "skill_name", "severity", "learning_suggestion", "created_at")


class RecommendationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)

    class Meta:
        model = Recommendation
        fields = (
            "id",
            "job",
            "match_score",
            "reasoning",
            "missing_skills",
            "strengths",
            "is_viewed",
            "created_at",
        )


class RecommendationDetailSerializer(RecommendationSerializer):
    skill_gaps = SkillGapSerializer(many=True, read_only=True)

    class Meta(RecommendationSerializer.Meta):
        fields = RecommendationSerializer.Meta.fields + ("skill_gaps",)

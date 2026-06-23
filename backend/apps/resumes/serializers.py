from rest_framework import serializers

from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = (
            "id",
            "original_filename",
            "raw_text",
            "structured_data",
            "skills",
            "education",
            "work_experience",
            "projects",
            "certifications",
            "ai_summary",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ResumeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ("file",)

    def validate_file(self, value):
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("Only PDF files are allowed.")
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size must be under 5MB.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        Resume.objects.filter(user=user, is_active=True).update(is_active=False)
        return Resume.objects.create(
            user=user,
            file=validated_data["file"],
            original_filename=validated_data["file"].name,
            is_active=True,
        )

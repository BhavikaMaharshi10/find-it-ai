from rest_framework import serializers

from apps.accounts.serializers import UserSerializer

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "headline",
            "location",
            "phone",
            "linkedin_url",
            "github_url",
            "avatar",
            "preferences",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")

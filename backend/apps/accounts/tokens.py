from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    def validate(self, attrs):
        # Accept 'email' key from frontend
        if "email" in attrs and User.USERNAME_FIELD not in attrs:
            attrs[User.USERNAME_FIELD] = attrs.pop("email")
        data = super().validate(attrs)
        from apps.accounts.serializers import UserSerializer

        data["user"] = UserSerializer(self.user).data
        return data

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.mixins import RateLimitMixin
from .constants import SECURITY_QUESTION
from .serializers import (
    ChangePasswordSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    SecurityQuestionSerializer,
    UserSerializer,
)
from .tokens import CustomTokenObtainPairSerializer

User = get_user_model()


class RegisterView(RateLimitMixin, generics.CreateAPIView):
    ratelimit_group = "auth_register"
    ratelimit_rate = "10/m"
    ratelimit_key = "ip"

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(RateLimitMixin, TokenObtainPairView):
    ratelimit_group = "auth_login"
    ratelimit_rate = "20/m"
    ratelimit_key = "ip"

    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        return Response({"message": "Logged out successfully."})


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"error": {"message": "Current password is incorrect."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"message": "Password changed successfully."})


class SecurityQuestionView(RateLimitMixin, APIView):
    """Return the security question for a registered email."""

    ratelimit_group = "auth_security_question"
    ratelimit_rate = "20/m"
    ratelimit_key = "ip"

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SecurityQuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"security_question": SECURITY_QUESTION})


class ResetPasswordView(RateLimitMixin, APIView):
    """Reset password using security question answer."""

    ratelimit_group = "auth_reset_password"
    ratelimit_rate = "10/m"
    ratelimit_key = "ip"

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successfully."})

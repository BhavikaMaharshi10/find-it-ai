import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        security_answer="football",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestAuthAPI:
    def test_register(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "new@example.com",
                "password": "securepass123",
                "password_confirm": "securepass123",
                "first_name": "New",
                "last_name": "User",
                "security_answer": "cricket",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert response.data["user"]["email"] == "new@example.com"

    def test_login(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "test@example.com", "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_me_authenticated(self, auth_client, user):
        response = auth_client.get("/api/v1/auth/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_me_unauthenticated(self, api_client):
        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_security_question(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/security-question/",
            {"email": user.email},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "favourite sport" in response.data["security_question"].lower()

    def test_reset_password_with_security_answer(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/reset-password/",
            {
                "email": user.email,
                "security_answer": "football",
                "new_password": "newpass123",
                "new_password_confirm": "newpass123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("newpass123")

    def test_reset_password_wrong_answer(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/reset-password/",
            {
                "email": user.email,
                "security_answer": "wrong",
                "new_password": "newpass123",
                "new_password_confirm": "newpass123",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestJobsAPI:
    def test_list_jobs_empty(self, auth_client):
        response = auth_client.get("/api/v1/jobs/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"] == []


@pytest.mark.django_db
class TestProfileAPI:
    def test_get_profile(self, auth_client, user):
        response = auth_client.get("/api/v1/profile/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["email"] == user.email

"""Custom User model with email-based authentication."""
import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from .constants import SECURITY_QUESTION


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, security_answer=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not security_answer:
            raise ValueError("Security answer is required")
        email = self.normalize_email(email)
        extra_fields.setdefault("username", email.split("@")[0])
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.set_security_answer(security_answer)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        security_answer = extra_fields.pop("security_answer", "admin")
        return self.create_user(
            email, password, security_answer=security_answer, **extra_fields
        )


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    security_answer_hash = models.CharField(max_length=128, default="")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email

    def set_security_answer(self, raw_answer: str) -> None:
        normalized = raw_answer.strip().lower()
        self.security_answer_hash = make_password(normalized)

    def check_security_answer(self, raw_answer: str) -> bool:
        normalized = raw_answer.strip().lower()
        return check_password(normalized, self.security_answer_hash)

    @property
    def security_question(self) -> str:
        return SECURITY_QUESTION


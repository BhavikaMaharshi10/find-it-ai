"""Shared DRF view mixins."""
from django.conf import settings
from django_ratelimit.core import is_ratelimited
from rest_framework.exceptions import Throttled


class RateLimitMixin:
    """Apply per-user (or per-IP) rate limits after authentication."""

    ratelimit_group: str | None = None
    ratelimit_rate: str = "60/m"
    ratelimit_key: str = "auto"

    def check_rate_limit(self, request) -> None:
        if not settings.RATELIMIT_ENABLE:
            return

        key = self.ratelimit_key
        if key == "auto":
            key = "user" if request.user.is_authenticated else "ip"

        group = self.ratelimit_group or self.__class__.__name__
        if is_ratelimited(
            request,
            group=group,
            key=key,
            rate=self.ratelimit_rate,
            increment=True,
        ):
            raise Throttled(detail="Too many requests. Please try again later.")

    def initial(self, request, *args, **kwargs):
        self.check_rate_limit(request)
        super().initial(request, *args, **kwargs)

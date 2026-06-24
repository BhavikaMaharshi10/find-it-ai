"""Core API views."""
from django.db import connection
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """Liveness/readiness probe for load balancers and Render."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        db_ok = True
        db_error = None
        try:
            connection.ensure_connection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as exc:
            db_ok = False
            db_error = str(exc)

        payload = {
            "status": "ok" if db_ok else "degraded",
            "database": "connected" if db_ok else "unavailable",
        }
        if db_error:
            payload["database_error"] = db_error

        status_code = 200 if db_ok else 503
        return Response(payload, status=status_code)

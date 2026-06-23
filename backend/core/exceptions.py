"""Custom DRF exception handler with structured error responses."""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger("finditai")


def custom_exception_handler(exc, context):
    """Return consistent JSON error payloads."""
    response = exception_handler(exc, context)

    if response is not None:
        error_payload = {
            "success": False,
            "error": {
                "code": response.status_code,
                "message": _extract_message(response.data),
                "details": response.data,
            },
        }
        response.data = error_payload
        return response

    logger.exception("Unhandled exception: %s", exc, exc_info=exc)
    return Response(
        {
            "success": False,
            "error": {
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred.",
            },
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def _extract_message(data):
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        for key, value in data.items():
            return f"{key}: {_extract_message(value)}"
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)

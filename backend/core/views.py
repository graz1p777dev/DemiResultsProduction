from django.conf import settings
from django.db import connections
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema, inline_serializer
import redis
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Health"],
        responses={
            200: inline_serializer(
                name="HealthCheckResponse",
                fields={
                    "status": serializers.CharField(),
                    "checks": serializers.DictField(child=serializers.CharField()),
                },
            ),
            503: OpenApiResponse(description="One or more dependencies are unavailable."),
        },
        examples=[
            OpenApiExample(
                "Healthy",
                value={"status": "ok", "checks": {"database": "ok", "redis": "ok"}},
                response_only=True,
            )
        ],
        description="Lightweight dependency health check for database and Redis.",
    )
    def get(self, request):
        checks = {"database": "ok", "redis": "ok"}
        status_code = 200
        try:
            connections["default"].cursor().execute("SELECT 1")
        except Exception:
            checks["database"] = "error"
            status_code = 503
        try:
            redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1).ping()
        except Exception:
            checks["redis"] = "error"
            status_code = 503
        return Response({"status": "ok" if status_code == 200 else "error", "checks": checks}, status=status_code)

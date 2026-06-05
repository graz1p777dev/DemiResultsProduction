import hmac

from django.conf import settings
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from common.permissions import IsOwnerAdminManager
from common.webhooks import is_valid_signature

from .models import AIConversation, AIMessage, AIWebhookLog
from .serializers import AIConversationSerializer, AIMessageSerializer, AIWebhookLogSerializer
from . import services


class N8NWebhookThrottle(SimpleRateThrottle):
    scope = "n8n"

    def get_cache_key(self, request, view):
        return self.get_ident(request)


class AIConversationViewSet(viewsets.ModelViewSet):
    queryset = AIConversation.objects.prefetch_related("messages").all()
    serializer_class = AIConversationSerializer
    permission_classes = [IsAuthenticated]


class AIMessageViewSet(viewsets.ModelViewSet):
    queryset = AIMessage.objects.select_related("conversation").all()
    serializer_class = AIMessageSerializer
    permission_classes = [IsAuthenticated]


class AIWebhookLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AIWebhookLog.objects.all().order_by("-created_at")
    serializer_class = AIWebhookLogSerializer
    permission_classes = [IsOwnerAdminManager]


@extend_schema(
    tags=["AI Assistant"],
    description="Search active products and return a safe AI-friendly payload.",
    responses={200: OpenApiResponse(description="Safe product list for AI usage.")},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ai_product_search(request):
    payload = {"query": request.query_params.get("q", "")}
    return Response({"products": services.search_products_for_ai(payload)})


def get_request_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@extend_schema(
    tags=["AI Assistant"],
    description="Secure n8n webhook. Requires Authorization: Token <N8N_API_TOKEN> and X-Demi-Signature HMAC-SHA256 over the raw body.",
    request=dict,
    examples=[
        OpenApiExample(
            "n8n product search",
            value={"phone": "+996700000000", "conversation_id": "tg-123", "message": "Нужен мягкий крем"},
            request_only=True,
        ),
    ],
    responses={
        200: OpenApiResponse(description="Webhook accepted."),
        403: OpenApiResponse(description="Invalid token or signature."),
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([N8NWebhookThrottle])
def n8n_webhook(request):
    token = request.headers.get("Authorization", "").replace("Token ", "", 1)
    signature = request.headers.get("X-Demi-Signature", "")
    token_ok = bool(settings.N8N_API_TOKEN and hmac.compare_digest(token, settings.N8N_API_TOKEN))
    signature_ok = is_valid_signature(request.body, signature)
    is_valid = token_ok and signature_ok

    log = AIWebhookLog.objects.create(payload=request.data, is_valid=is_valid, ip_address=get_request_ip(request))
    if not is_valid:
        log.response = {"detail": "Invalid webhook credentials."}
        log.save(update_fields=["response", "updated_at"])
        return Response(log.response, status=status.HTTP_403_FORBIDDEN)

    payload = request.data if isinstance(request.data, dict) else {}
    response = services.build_ai_response_payload(payload, log.pk)
    log.response = response
    log.save(update_fields=["response", "updated_at"])
    return Response(response)

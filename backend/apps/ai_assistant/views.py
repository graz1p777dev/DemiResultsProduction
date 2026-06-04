from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle

from common.webhooks import is_valid_signature

from .models import AIConversation, AIMessage, AIWebhookLog
from .serializers import AIConversationSerializer, AIMessageSerializer, AIWebhookLogSerializer


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
    permission_classes = [IsAuthenticated]


@extend_schema(
    request=dict,
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
    token_ok = bool(settings.N8N_API_TOKEN and token == settings.N8N_API_TOKEN)
    signature_ok = is_valid_signature(request.body, signature)
    is_valid = token_ok and signature_ok

    log = AIWebhookLog.objects.create(payload=request.data, is_valid=is_valid)
    if not is_valid:
        log.response = {"detail": "Invalid webhook credentials."}
        log.save(update_fields=["response", "updated_at"])
        return Response(log.response, status=status.HTTP_403_FORBIDDEN)

    response = {"ok": True, "log_id": log.pk}
    log.response = response
    log.save(update_fields=["response", "updated_at"])
    return Response(response)

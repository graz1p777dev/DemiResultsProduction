from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AIConversationViewSet, AIMessageViewSet, AIWebhookLogViewSet, n8n_webhook

router = DefaultRouter()
router.register("conversations", AIConversationViewSet)
router.register("messages", AIMessageViewSet)
router.register("webhook-logs", AIWebhookLogViewSet)

urlpatterns = [
    path("webhook/", n8n_webhook, name="n8n-webhook"),
] + router.urls


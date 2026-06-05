from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AIConversationViewSet, AIMessageViewSet, AIWebhookLogViewSet, ai_product_search, n8n_webhook

router = DefaultRouter()
router.register("conversations", AIConversationViewSet)
router.register("messages", AIMessageViewSet)
router.register("webhook-logs", AIWebhookLogViewSet)

urlpatterns = [
    path("webhook/", n8n_webhook, name="n8n-webhook"),
    path("products/search/", ai_product_search, name="ai-product-search"),
] + router.urls

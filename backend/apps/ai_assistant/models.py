from django.conf import settings
from django.db import models

from common.models import TimeStampedModel
from common.validators import kyrgyz_phone_validator


class AIConversation(TimeStampedModel):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="ai_conversations")
    external_id = models.CharField(max_length=128, blank=True)
    customer_phone = models.CharField(max_length=13, blank=True, db_index=True, validators=[kyrgyz_phone_validator])
    telegram_username = models.CharField(max_length=128, blank=True, db_index=True)
    status = models.CharField(max_length=32, default="OPEN")

    def __str__(self):
        return f"AI conversation #{self.pk}"


class AIMessage(TimeStampedModel):
    class Role(models.TextChoices):
        USER = "USER", "User"
        ASSISTANT = "ASSISTANT", "Assistant"
        SYSTEM = "SYSTEM", "System"
        STAFF = "STAFF", "Staff"

    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=32, choices=Role.choices)
    content = models.TextField()
    payload = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.role}: {self.content[:40]}"


class AIWebhookLog(TimeStampedModel):
    source = models.CharField(max_length=64, default="n8n")
    payload = models.JSONField(default=dict, blank=True)
    is_valid = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    response = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Webhook {self.source} valid={self.is_valid}"

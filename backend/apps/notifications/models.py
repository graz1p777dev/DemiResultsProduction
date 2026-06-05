from django.conf import settings
from django.db import models

from common.models import CreatedByModel


class Notification(CreatedByModel):
    class Channel(models.TextChoices):
        IN_APP = "IN_APP", "In app"
        SMS = "SMS", "SMS"
        EMAIL = "EMAIL", "Email"
        PUSH = "PUSH", "Push"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    channel = models.CharField(max_length=32, choices=Channel.choices, default=Channel.IN_APP)
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivery_error = models.TextField(blank=True)
    provider_reference = models.CharField(max_length=128, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["channel", "sent_at"]),
        ]

    def __str__(self):
        return self.title

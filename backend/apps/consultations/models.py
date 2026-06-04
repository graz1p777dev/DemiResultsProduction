from django.conf import settings
from django.db import models

from common.models import CreatedByModel


class Consultation(CreatedByModel):
    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        CONFIRMED = "CONFIRMED", "Confirmed"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="consultations")
    consultant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_consultations")
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.REQUESTED)
    questionnaire = models.JSONField(default=dict, blank=True)
    recommendations = models.TextField(blank=True)

    def __str__(self):
        return f"Consultation #{self.pk}"


class ConsultationMessage(CreatedByModel):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="consultation_messages")
    text = models.TextField()

    def __str__(self):
        return f"Message #{self.pk}"


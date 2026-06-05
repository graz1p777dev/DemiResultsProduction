import logging

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import Notification

logger = logging.getLogger(__name__)


@shared_task
def mark_notification_sent(notification_id):
    notification = Notification.objects.get(pk=notification_id)
    if notification.channel == Notification.Channel.SMS:
        phone = notification.user.phone or "missing-phone"
        logger.info("DemiResults notification SMS to %s: %s", phone, notification.body)
        print(f"DemiResults notification SMS to {phone}: {notification.body}", flush=True)
        notification.provider_reference = f"{settings.SMS_PROVIDER}:{notification.id}"
    notification.sent_at = timezone.now()
    notification.delivery_error = ""
    notification.save(update_fields=["sent_at", "delivery_error", "provider_reference", "updated_at"])
    return {"notification_id": notification.id, "channel": notification.channel, "sent_at": notification.sent_at.isoformat()}

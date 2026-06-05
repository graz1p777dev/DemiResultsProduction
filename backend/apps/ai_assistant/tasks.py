from celery import shared_task

from .models import AIWebhookLog


@shared_task
def cleanup_invalid_webhook_logs(limit=1000):
    ids = list(AIWebhookLog.objects.filter(is_valid=False).order_by("created_at").values_list("id", flat=True)[:limit])
    deleted, _ = AIWebhookLog.objects.filter(id__in=ids).delete()
    return {"deleted": deleted}

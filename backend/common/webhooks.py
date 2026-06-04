import hmac
from hashlib import sha256

from django.conf import settings


def is_valid_signature(raw_body: bytes, signature: str) -> bool:
    if not settings.N8N_WEBHOOK_SECRET or not signature:
        return False
    expected = hmac.new(
        settings.N8N_WEBHOOK_SECRET.encode(),
        raw_body,
        sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


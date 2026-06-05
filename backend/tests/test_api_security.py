import hashlib
import hmac
import json

import pytest
from django.core.exceptions import ValidationError
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient

from apps.audit.models import AuditLog
from apps.ai_assistant.models import AIConversation, AIMessage, AIWebhookLog

from .factories import make_product, make_user


@pytest.mark.django_db
def test_user_phone_accepts_only_kyrgyz_format():
    user = make_user("phone-client", role="CLIENT")
    user.phone = "+996123123123"
    user.full_clean()

    user.phone = "996123123123"
    with pytest.raises(ValidationError):
        user.full_clean()

    user.phone = "+79991231231"
    with pytest.raises(ValidationError):
        user.full_clean()


@pytest.mark.django_db
def test_n8n_webhook_requires_token_and_signature(settings):
    settings.N8N_API_TOKEN = "token"
    settings.N8N_WEBHOOK_SECRET = "secret"
    client = APIClient()
    response = client.post("/api/ai/webhook/", {"message": "cream"}, format="json")

    assert response.status_code == 403
    assert AIWebhookLog.objects.filter(is_valid=False).exists()


@pytest.mark.django_db
def test_n8n_webhook_saves_conversation_and_returns_products(settings):
    settings.N8N_API_TOKEN = "token"
    settings.N8N_WEBHOOK_SECRET = "secret"
    user = make_user("ai-client", role="CLIENT")
    user.phone = "+996700000000"
    user.save(update_fields=["phone"])
    make_product(created_by=user, sku="CREAM-1")
    payload = {"phone": "+996700000000", "message": "Product", "conversation_id": "tg-1"}
    body = json.dumps(payload).encode()
    signature = hmac.new(settings.N8N_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()

    client = APIClient()
    response = client.post(
        "/api/ai/webhook/",
        data=body,
        content_type="application/json",
        HTTP_AUTHORIZATION="Token token",
        HTTP_X_DEMI_SIGNATURE=signature,
    )

    assert response.status_code == 200
    assert response.data["client_id"] == user.id
    assert response.data["products"]
    assert AIConversation.objects.filter(client=user, external_id="tg-1").exists()
    assert AIMessage.objects.filter(content="Product").exists()


@pytest.mark.django_db
def test_ai_client_lookup_by_google_id():
    from apps.ai_assistant import services

    user = make_user("external-client", role="CLIENT")
    user.email = "external@example.com"
    user.google_id = "google-777"
    user.save(update_fields=["email", "google_id"])

    found = services.find_client_for_ai({"google_id": "google-777"})

    assert found == user


@pytest.mark.django_db
def test_audit_middleware_records_authenticated_write_request():
    manager = make_user("audit-manager", role="MANAGER")
    client = APIClient()
    client.force_authenticate(manager)

    response = client.post(
        "/api/products/categories/",
        {"name": "Audit Category", "slug": "audit-category"},
        format="json",
    )

    assert response.status_code == 201
    assert AuditLog.objects.filter(actor=manager, action__startswith="POST /api/products/categories/").exists()


@pytest.mark.django_db
def test_client_cannot_read_other_client_profile():
    owner = make_user("owner", role="OWNER")
    client_one = make_user("client-one", role="CLIENT")
    client_two = make_user("client-two", role="CLIENT")
    from apps.users.models import ClientProfile

    profile_one = ClientProfile.objects.create(user=client_one)
    ClientProfile.objects.create(user=client_two)

    api = APIClient()
    api.force_authenticate(client_two)
    response = api.get(f"/api/users/client-profiles/{profile_one.id}/")

    assert response.status_code == 404

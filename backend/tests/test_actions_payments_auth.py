import pytest
from rest_framework.test import APIClient
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from unittest.mock import patch

from apps.inventory.models import StockLevel
from apps.notifications.models import Notification
from apps.notifications.tasks import mark_notification_sent
from apps.reports.tasks import cleanup_old_database_backups, cleanup_old_report_exports
from apps.orders import services as order_service
from apps.bonuses import services as bonus_service
from apps.payments.models import Payment
from apps.payments import services as payment_service
from apps.users.models import ClientProfile, PhoneAuthCode

from .factories import make_product, make_user, make_warehouse, receive_stock


@pytest.mark.django_db
def test_inventory_receive_action_creates_stock():
    user = make_user("warehouse-action", role="WAREHOUSE")
    product = make_product(created_by=user, sku="SKU-ACTION")
    warehouse = make_warehouse(created_by=user, code="ACT")
    client = APIClient()
    client.force_authenticate(user)

    response = client.post(
        "/api/inventory/stock-movements/receive/",
        {"product": product.id, "destination_warehouse": warehouse.id, "quantity": 4, "reason": "Action receipt"},
        format="json",
    )

    assert response.status_code == 201
    assert StockLevel.objects.get(product=product, warehouse=warehouse).quantity == 4


@pytest.mark.django_db
def test_payment_mark_paid_and_refund_services():
    cashier = make_user("payment-cashier", role="CASHIER")
    client_user = make_user("payment-client", role="CLIENT")
    warehouse = make_warehouse(created_by=cashier, code="PAY")
    order = order_service.create_order(client=client_user, warehouse=warehouse, created_by=client_user)
    payment = payment_service.create_payment(amount="100.00", method=Payment.Method.CASH, order=order, created_by=cashier)

    paid = payment_service.mark_payment_paid(payment=payment, created_by=cashier)
    refund = payment_service.refund_payment(payment=paid, created_by=cashier, reason="Test refund")
    paid.refresh_from_db()

    assert paid.status == Payment.Status.REFUNDED
    assert refund.amount == paid.amount


@pytest.mark.django_db
def test_local_payment_api_create_and_confirm():
    cashier = make_user("local-payment-cashier", role="CASHIER")
    client_user = make_user("local-payment-client", role="CLIENT")
    warehouse = make_warehouse(created_by=cashier, code="LPAY")
    order = order_service.create_order(client=client_user, warehouse=warehouse, created_by=client_user)
    api = APIClient()
    api.force_authenticate(cashier)

    create_response = api.post("/api/payments/payments/local/", {"order": order.id, "amount": "150.00"}, format="json")
    payment_id = create_response.data["id"]
    confirm_response = api.post(f"/api/payments/payments/{payment_id}/confirm-local/", {}, format="json")

    assert create_response.status_code == 201
    assert create_response.data["provider"] == "local"
    assert create_response.data["provider_reference"].startswith("LOCAL-")
    assert confirm_response.status_code == 200
    assert confirm_response.data["status"] == Payment.Status.PAID


@pytest.mark.django_db
def test_password_change_and_logout_endpoints():
    user = make_user("auth-actions", role="CLIENT", password="OldPass12345!")
    api = APIClient()
    token_response = api.post("/api/auth/token/", {"username": user.email, "password": "OldPass12345!"}, format="json")
    assert token_response.status_code == 200

    api.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")
    change_response = api.post(
        "/api/auth/password/change/",
        {"old_password": "OldPass12345!", "new_password": "NewPass12345!"},
        format="json",
    )
    logout_response = api.post("/api/auth/logout/", {"refresh": token_response.data["refresh"]}, format="json")

    assert change_response.status_code == 204
    assert logout_response.status_code == 204


@pytest.mark.django_db
def test_password_reset_request_and_confirm(mailoutbox):
    user = make_user("reset-client", role="CLIENT", password="OldPass12345!")
    api = APIClient()

    request_response = api.post("/api/auth/password/reset/", {"email": user.email}, format="json")
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    confirm_response = api.post(
        "/api/auth/password/reset/confirm/",
        {"uid": uid, "token": token, "new_password": "NewPass12345!"},
        format="json",
    )
    user.refresh_from_db()

    assert request_response.status_code == 200
    assert len(mailoutbox) == 1
    assert confirm_response.status_code == 204
    assert user.check_password("NewPass12345!")


@pytest.mark.django_db
def test_register_endpoint_validates_password_and_returns_tokens():
    api = APIClient()

    weak_response = api.post(
        "/api/auth/register/",
        {"email": "weak@example.com", "password": "12345678"},
        format="json",
    )
    response = api.post(
        "/api/auth/register/",
        {
            "email": "registered@example.com",
            "phone": "+996700222333",
            "password": "StrongPass12345!",
            "first_name": "Ainara",
        },
        format="json",
    )
    user = get_user_model().objects.get(email="registered@example.com")

    assert weak_response.status_code == 400
    assert response.status_code == 201
    assert response.data["access"]
    assert response.data["refresh"]
    assert user.role == get_user_model().Role.CLIENT
    assert ClientProfile.objects.filter(user=user).exists()


@pytest.mark.django_db
@patch("apps.users.auth_services._generate_phone_code", return_value="123456")
def test_phone_auth_code_is_logged_and_creates_client(mock_code, capsys):
    api = APIClient()

    request_response = api.post("/api/auth/phone/request-code/", {"phone": "+996700111222"}, format="json")
    output = capsys.readouterr().out
    verify_response = api.post("/api/auth/phone/verify/", {"phone": "+996700111222", "code": "123456"}, format="json")
    user = get_user_model().objects.get(phone="+996700111222")

    assert request_response.status_code == 200
    assert "DemiResults SMS code for +996700111222: 123456" in output
    assert verify_response.status_code == 200
    assert verify_response.data["access"]
    assert verify_response.data["refresh"]
    assert user.role == get_user_model().Role.CLIENT
    assert ClientProfile.objects.filter(user=user).exists()
    assert PhoneAuthCode.objects.get(phone="+996700111222").consumed_at is not None


@pytest.mark.django_db
@patch("apps.users.auth_services._generate_phone_code", return_value="123456")
def test_phone_auth_rejects_invalid_code(mock_code):
    api = APIClient()

    api.post("/api/auth/phone/request-code/", {"phone": "+996700111223"}, format="json")
    verify_response = api.post("/api/auth/phone/verify/", {"phone": "+996700111223", "code": "000000"}, format="json")

    assert verify_response.status_code == 400
    assert verify_response.data["code"] == "invalid_phone_code"


@pytest.mark.django_db
def test_notification_object_scope_and_task():
    owner = make_user("notify-owner", role="OWNER")
    client_one = make_user("notify-client-one", role="CLIENT")
    client_two = make_user("notify-client-two", role="CLIENT")
    visible = Notification.objects.create(user=client_one, title="Visible", body="One", created_by=owner)
    Notification.objects.create(user=client_two, title="Hidden", body="Two", created_by=owner)
    api = APIClient()
    api.force_authenticate(client_one)

    response = api.get("/api/notifications/notifications/")
    task_result = mark_notification_sent(visible.id)
    visible.refresh_from_db()

    assert response.status_code == 200
    assert len(response.data["results"]) == 1 if isinstance(response.data, dict) and "results" in response.data else len(response.data) == 1
    assert task_result["notification_id"] == visible.id
    assert visible.sent_at is not None


@pytest.mark.django_db
def test_report_cleanup_task_runs():
    result = cleanup_old_report_exports(days=0)
    backup_cleanup = cleanup_old_database_backups(days=0)

    assert "deleted" in result
    assert "deleted" in backup_cleanup


@pytest.mark.django_db
def test_health_endpoint():
    response = APIClient().get("/api/health/")

    assert response.status_code == 200
    assert response.data["status"] == "ok"


@pytest.mark.django_db
def test_client_catalog_hides_staff_fields():
    product = make_product(sku="CATALOG", price="250.00", cost="100.00")

    response = APIClient().get("/api/catalog/products/")
    row = response.data["results"][0] if isinstance(response.data, dict) and "results" in response.data else response.data[0]

    assert response.status_code == 200
    assert row["id"] == product.id
    assert "cost_price" not in row
    assert "created_by" not in row


@pytest.mark.django_db
def test_me_profile_patch_and_bonus_scope():
    client = make_user("me-client", role="CLIENT")
    other_client = make_user("me-other-client", role="CLIENT")
    bonus_service.accrue_bonus(client=client, amount="25.00", reason="Own bonus")
    bonus_service.accrue_bonus(client=other_client, amount="99.00", reason="Other bonus")
    api = APIClient()
    api.force_authenticate(client)

    profile_response = api.patch("/api/me/", {"first_name": "Ainara", "client_profile": {"skin_type": "dry"}}, format="json")
    bonus_response = api.get("/api/me/bonuses/")
    client.refresh_from_db()

    assert profile_response.status_code == 200
    assert profile_response.data["first_name"] == "Ainara"
    assert profile_response.data["client_profile"]["skin_type"] == "dry"
    assert bonus_response.status_code == 200
    assert bonus_response.data["balance"] == "25.00"
    assert len(bonus_response.data["transactions"]) == 1


@pytest.mark.django_db
def test_client_order_create_and_cancel():
    client = make_user("me-order-client", role="CLIENT")
    product = make_product(sku="ME-ORDER", price="320.00")
    api = APIClient()
    api.force_authenticate(client)

    create_response = api.post(
        "/api/me/orders/",
        {"items": [{"product": product.id, "quantity": 2}], "comment": "Client order"},
        format="json",
    )
    order_id = create_response.data["id"]
    list_response = api.get("/api/me/orders/")
    cancel_response = api.post(f"/api/me/orders/{order_id}/cancel/", {"comment": "Changed mind"}, format="json")

    assert create_response.status_code == 201
    assert create_response.data["total"] == "640.00"
    assert list_response.status_code == 200
    assert cancel_response.status_code == 200
    assert cancel_response.data["status"] == "CANCELLED"


@pytest.mark.django_db
def test_client_consultation_messages_are_scoped_to_owner():
    client = make_user("me-consult-client", role="CLIENT")
    other_client = make_user("me-consult-other", role="CLIENT")
    api = APIClient()
    api.force_authenticate(client)

    create_response = api.post(
        "/api/me/consultations/",
        {"scheduled_at": "2026-07-01T10:00:00+06:00", "questionnaire": {"concern": "dryness"}},
        format="json",
    )
    consultation_id = create_response.data["id"]
    message_response = api.post(f"/api/me/consultations/{consultation_id}/messages/", {"text": "Need help"}, format="json")

    other_api = APIClient()
    other_api.force_authenticate(other_client)
    hidden_response = other_api.get(f"/api/me/consultations/{consultation_id}/")

    assert create_response.status_code == 201
    assert message_response.status_code == 201
    assert hidden_response.status_code == 404

from decimal import Decimal
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.audit.services import log_event

from .models import Payment, PaymentRefund


@transaction.atomic
def create_payment(
    *,
    amount,
    method,
    order=None,
    sale=None,
    created_by=None,
    external_id="",
    status=Payment.Status.PENDING,
    provider="local",
    provider_reference="",
    provider_payload=None,
):
    if not order and not sale:
        raise ValidationError("Payment must be linked to an order or sale.")
    payment = Payment.objects.create(
        order=order,
        sale=sale,
        method=method,
        status=status,
        amount=amount,
        provider=provider,
        provider_reference=provider_reference,
        provider_payload=provider_payload or {},
        external_id=external_id,
        paid_at=timezone.now() if status == Payment.Status.PAID else None,
        created_by=created_by,
    )
    log_event(actor=created_by, action="payment.created", entity_type="payment", entity_id=payment.id, metadata={"amount": str(amount), "method": method})
    return payment


@transaction.atomic
def create_local_payment(*, amount, order=None, sale=None, created_by=None):
    if settings.PAYMENT_PROVIDER != "local":
        raise ValidationError("Local payment provider is disabled.")
    reference = f"LOCAL-{uuid.uuid4().hex[:16].upper()}"
    status = Payment.Status.PAID if settings.LOCAL_PAYMENT_AUTO_CAPTURE else Payment.Status.PENDING
    payment = create_payment(
        amount=amount,
        method=Payment.Method.ONLINE,
        order=order,
        sale=sale,
        created_by=created_by,
        provider="local",
        provider_reference=reference,
        provider_payload={"provider": "local", "mode": "development"},
        external_id=reference if status == Payment.Status.PAID else "",
        status=status,
    )
    log_event(actor=created_by, action="payment.local.created", entity_type="payment", entity_id=payment.id, metadata={"reference": reference})
    return payment


@transaction.atomic
def mark_payment_paid(*, payment, created_by=None, external_id=""):
    payment = Payment.objects.select_for_update().get(pk=payment.pk)
    if payment.status == Payment.Status.REFUNDED:
        raise ValidationError("Refunded payment cannot be marked as paid.")
    payment.status = Payment.Status.PAID
    payment.paid_at = timezone.now()
    if external_id:
        payment.external_id = external_id
    payment.save(update_fields=["status", "paid_at", "external_id", "updated_at"])
    log_event(actor=created_by, action="payment.paid", entity_type="payment", entity_id=payment.id)
    return payment


@transaction.atomic
def fail_local_payment(*, payment, created_by=None, reason=""):
    payment = Payment.objects.select_for_update().get(pk=payment.pk)
    if payment.provider != "local":
        raise ValidationError("Only local provider payments can be failed here.")
    if payment.status != Payment.Status.PENDING:
        raise ValidationError("Only pending local payments can be failed.")
    payment.status = Payment.Status.FAILED
    payment.provider_payload = {**payment.provider_payload, "failure_reason": reason}
    payment.save(update_fields=["status", "provider_payload", "updated_at"])
    log_event(actor=created_by, action="payment.local.failed", entity_type="payment", entity_id=payment.id, metadata={"reason": reason})
    return payment


@transaction.atomic
def refund_payment(*, payment, amount=None, reason="", created_by=None):
    payment = Payment.objects.select_for_update().get(pk=payment.pk)
    if payment.status != Payment.Status.PAID:
        raise ValidationError("Only paid payments can be refunded.")
    amount = Decimal(amount) if amount is not None else payment.amount
    if amount <= 0 or amount > payment.amount:
        raise ValidationError("Refund amount must be positive and cannot exceed payment amount.")
    refund = PaymentRefund.objects.create(payment=payment, amount=amount, reason=reason, created_by=created_by)
    payment.status = Payment.Status.REFUNDED
    payment.save(update_fields=["status", "updated_at"])
    log_event(actor=created_by, action="payment.refunded", entity_type="payment", entity_id=payment.id, metadata={"amount": str(amount)})
    return refund

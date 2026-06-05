from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from .models import BonusAccount, BonusTransaction


def get_or_create_account(client):
    account, _ = BonusAccount.objects.get_or_create(client=client)
    return account


@transaction.atomic
def accrue_bonus(*, client, amount, created_by=None, reason="Bonus accrual"):
    amount = Decimal(amount)
    if amount <= 0:
        raise ValidationError("Bonus amount must be positive.")
    account = BonusAccount.objects.select_for_update().get(pk=get_or_create_account(client).pk)
    account.balance = F("balance") + amount
    account.save(update_fields=["balance", "updated_at"])
    account.refresh_from_db(fields=["balance"])
    return BonusTransaction.objects.create(
        account=account,
        transaction_type=BonusTransaction.Type.ACCRUAL,
        amount=amount,
        reason=reason,
        created_by=created_by,
    )


@transaction.atomic
def spend_bonus(*, client, amount, created_by=None, reason="Bonus spend"):
    amount = Decimal(amount)
    if amount <= 0:
        raise ValidationError("Bonus amount must be positive.")
    account = BonusAccount.objects.select_for_update().get(pk=get_or_create_account(client).pk)
    if account.balance < amount:
        raise ValidationError("Insufficient bonus balance.")
    account.balance = F("balance") - amount
    account.save(update_fields=["balance", "updated_at"])
    account.refresh_from_db(fields=["balance"])
    return BonusTransaction.objects.create(
        account=account,
        transaction_type=BonusTransaction.Type.SPEND,
        amount=amount,
        reason=reason,
        created_by=created_by,
    )


@transaction.atomic
def rollback_bonus(*, transaction, created_by=None, reason="Bonus rollback"):
    if transaction.transaction_type == BonusTransaction.Type.ACCRUAL:
        return spend_bonus(client=transaction.account.client, amount=transaction.amount, created_by=created_by, reason=reason)
    if transaction.transaction_type == BonusTransaction.Type.SPEND:
        return accrue_bonus(client=transaction.account.client, amount=transaction.amount, created_by=created_by, reason=reason)
    raise ValidationError("Only accrual and spend transactions can be rolled back.")


def calculate_bonus_for_sale(sale):
    return max(sale.total * Decimal("0.03"), Decimal("0")).quantize(Decimal("0.01"))


def calculate_bonus_for_order(order):
    return max(order.total * Decimal("0.03"), Decimal("0")).quantize(Decimal("0.01"))

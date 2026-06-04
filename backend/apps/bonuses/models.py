from django.conf import settings
from django.db import models

from common.models import CreatedByModel, TimeStampedModel


class BonusAccount(TimeStampedModel):
    client = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bonus_account")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Bonus account {self.client_id}: {self.balance}"


class BonusTransaction(CreatedByModel):
    class Type(models.TextChoices):
        ACCRUAL = "ACCRUAL", "Accrual"
        SPEND = "SPEND", "Spend"
        CORRECTION = "CORRECTION", "Correction"

    account = models.ForeignKey(BonusAccount, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=32, choices=Type.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.transaction_type} {self.amount}"


class PromoCode(CreatedByModel):
    code = models.CharField(max_length=64, unique=True)
    discount_percent = models.PositiveIntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.code


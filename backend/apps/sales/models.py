from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.inventory.models import StockMovement
from apps.products.models import Product
from common.models import CreatedByModel


class Sale(CreatedByModel):
    class Status(models.TextChoices):
        COMPLETED = "COMPLETED", "Completed"
        REFUNDED = "REFUNDED", "Refunded"
        CANCELLED = "CANCELLED", "Cancelled"

    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sales")
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="client_sales")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.COMPLETED)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def recalculate_totals(self):
        subtotal = sum((item.line_total for item in self.items.all()), Decimal("0"))
        self.subtotal = subtotal
        self.total = max(subtotal - self.discount_total - self.bonus_spent, Decimal("0"))
        self.save(update_fields=["subtotal", "total", "updated_at"])

    def __str__(self):
        return f"Sale #{self.pk}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Sale items are immutable after creation.")
        self.unit_price = self.product.price
        with transaction.atomic():
            super().save(*args, **kwargs)
            StockMovement.objects.create(
                product=self.product,
                movement_type=StockMovement.MovementType.SALE,
                quantity=self.quantity,
                reason="POS sale",
                reference=f"sale:{self.sale_id}",
                created_by=self.sale.cashier,
            )
            self.sale.recalculate_totals()

    def __str__(self):
        return f"{self.product} x {self.quantity}"


class SaleReturn(CreatedByModel):
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="returns")
    reason = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Sale returns are immutable after creation.")
        with transaction.atomic():
            super().save(*args, **kwargs)
            for item in self.sale.items.all():
                StockMovement.objects.create(
                    product=item.product,
                    movement_type=StockMovement.MovementType.RETURN,
                    quantity=item.quantity,
                    reason="Sale return",
                    reference=f"sale_return:{self.pk}",
                    created_by=self.created_by,
                )
            self.sale.status = Sale.Status.REFUNDED
            self.sale.save(update_fields=["status", "updated_at"])

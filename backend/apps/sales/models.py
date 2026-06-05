from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from apps.inventory.models import Warehouse
from apps.products.models import Product, ProductBatch, ProductVariant
from common.models import CreatedByModel


class Sale(CreatedByModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        COMPLETED = "COMPLETED", "Completed"
        PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED", "Partially refunded"
        REFUNDED = "REFUNDED", "Refunded"
        CANCELLED = "CANCELLED", "Cancelled"

    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sales")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True, related_name="sales")
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="client_sales")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.COMPLETED)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bonus_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.status != self.Status.DRAFT and not self.warehouse_id:
            raise ValidationError("Warehouse is required for completed sales.")

    def recalculate_totals(self):
        from .services import update_sale_totals

        return update_sale_totals(self)

    def save(self, *args, **kwargs):
        if self.status == self.Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale #{self.pk}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True)
    batch = models.ForeignKey(ProductBatch, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    @property
    def cost_total(self):
        return self.unit_cost * self.quantity

    @property
    def profit(self):
        return self.line_total - self.cost_total

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        if self.variant and self.variant.product_id != self.product_id:
            raise ValidationError("Variant must belong to selected product.")
        if self.batch and self.batch.product_id != self.product_id:
            raise ValidationError("Batch must belong to selected product.")
        if self.sale.status in {Sale.Status.CANCELLED, Sale.Status.REFUNDED}:
            raise ValidationError("Cannot add items to cancelled or refunded sale.")
        if not self.sale.warehouse_id:
            raise ValidationError("Sale warehouse is required before adding items.")

    def save(self, *args, **kwargs):
        if getattr(self, "_skip_sale_item_service", False):
            return super().save(*args, **kwargs)
        if self.pk:
            raise ValidationError("Sale items are immutable after creation.")
        from .services import add_sale_item

        return add_sale_item(
            sale=self.sale,
            product=self.product,
            variant=self.variant,
            batch=self.batch,
            quantity=self.quantity,
        )

    def __str__(self):
        return f"{self.product} x {self.quantity}"


class SaleReturn(CreatedByModel):
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name="returns")
    reason = models.TextField(blank=True)
    total_refund = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sale"], name="uniq_sale_return_per_sale"),
        ]

    def save(self, *args, **kwargs):
        if getattr(self, "_skip_sale_return_service", False):
            return super().save(*args, **kwargs)
        if self.pk:
            raise ValidationError("Sale returns are immutable after creation.")
        from .services import refund_sale

        return refund_sale(sale=self.sale, created_by=self.created_by, reason=self.reason)

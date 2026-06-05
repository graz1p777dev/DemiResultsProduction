from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.inventory.models import Warehouse
from apps.products.models import Product
from apps.products.models import ProductBatch, ProductVariant
from common.models import CreatedByModel


class Order(CreatedByModel):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PACKING = "PACKING", "Packing"
        DELIVERING = "DELIVERING", "Delivering"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True, related_name="orders")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.CREATED)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comment = models.TextField(blank=True)
    stock_reserved = models.BooleanField(default=False)

    ALLOWED_TRANSITIONS = {
        Status.CREATED: {Status.CONFIRMED, Status.CANCELLED},
        Status.CONFIRMED: {Status.PACKING, Status.CANCELLED},
        Status.PACKING: {Status.DELIVERING},
        Status.DELIVERING: {Status.COMPLETED},
        Status.COMPLETED: set(),
        Status.CANCELLED: set(),
    }
    CANCELLABLE_STATUSES = {Status.CREATED, Status.CONFIRMED}

    def clean(self):
        if not self.pk:
            return
        previous = Order.objects.filter(pk=self.pk).values_list("status", flat=True).first()
        if previous and previous != self.status and self.status not in self.ALLOWED_TRANSITIONS.get(previous, set()):
            raise ValidationError(f"Cannot change order status from {previous} to {self.status}.")

    def recalculate_totals(self):
        from .services import update_order_totals

        return update_order_totals(self)

    def cancel(self):
        from .services import cancel_order

        return cancel_order(order=self)

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True)
    batch = models.ForeignKey(ProductBatch, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        if self.variant and self.variant.product_id != self.product_id:
            raise ValidationError("Variant must belong to selected product.")
        if self.batch and self.batch.product_id != self.product_id:
            raise ValidationError("Batch must belong to selected product.")
        if self.order.status not in {Order.Status.CREATED, Order.Status.CONFIRMED}:
            raise ValidationError("Order items can be changed only before packing.")

    def save(self, *args, **kwargs):
        if getattr(self, "_skip_order_item_service", False):
            return super().save(*args, **kwargs)
        if self.pk:
            raise ValidationError("Order items are immutable after creation.")
        from .services import add_order_item

        return add_order_item(
            order=self.order,
            product=self.product,
            variant=self.variant,
            batch=self.batch,
            quantity=self.quantity,
        )

    def __str__(self):
        return f"{self.product} x {self.quantity}"


class OrderStatusHistory(CreatedByModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    from_status = models.CharField(max_length=32, choices=Order.Status.choices, blank=True)
    to_status = models.CharField(max_length=32, choices=Order.Status.choices)
    comment = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "created_at"]),
            models.Index(fields=["to_status"]),
        ]

    def __str__(self):
        return f"Order {self.order_id}: {self.from_status} -> {self.to_status}"

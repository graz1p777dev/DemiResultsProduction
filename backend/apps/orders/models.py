from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.products.models import Product
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
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.CREATED)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    comment = models.TextField(blank=True)

    def recalculate_totals(self):
        subtotal = sum((item.line_total for item in self.items.all()), Decimal("0"))
        self.subtotal = subtotal
        self.total = max(subtotal + self.delivery_price - self.discount_total, Decimal("0"))
        self.save(update_fields=["subtotal", "total", "updated_at"])

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Order items are immutable after creation.")
        self.unit_price = self.product.price
        super().save(*args, **kwargs)
        self.order.recalculate_totals()

    def __str__(self):
        return f"{self.product} x {self.quantity}"

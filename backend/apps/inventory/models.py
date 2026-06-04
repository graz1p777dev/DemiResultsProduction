from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F

from apps.products.models import Product
from common.models import CreatedByModel


class StockMovement(CreatedByModel):
    class MovementType(models.TextChoices):
        IN = "IN", "Receipt"
        OUT = "OUT", "Write-off"
        SALE = "SALE", "Sale"
        RETURN = "RETURN", "Return"
        INVENTORY = "INVENTORY", "Inventory correction"

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="stock_movements")
    movement_type = models.CharField(max_length=32, choices=MovementType.choices)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError("Stock movements are immutable after creation.")
        self.full_clean()
        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=self.product_id)
            delta = self.quantity if self.movement_type in {self.MovementType.IN, self.MovementType.RETURN} else -self.quantity
            if self.movement_type == self.MovementType.INVENTORY:
                delta = self.quantity - product.stock_quantity
            if delta < 0 and product.stock_quantity < abs(delta):
                raise ValidationError("Insufficient stock for this movement.")
            super().save(*args, **kwargs)
            Product.objects.filter(pk=self.product_id).update(stock_quantity=F("stock_quantity") + delta)

    def __str__(self):
        return f"{self.product} {self.movement_type} {self.quantity}"

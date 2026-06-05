from django.core.exceptions import ValidationError
from django.db import models

from apps.products.models import Product, ProductBatch, ProductVariant
from common.models import CreatedByModel


class Branch(CreatedByModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32, unique=True)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Warehouse(CreatedByModel):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="warehouses")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["branch__name", "name"]
        constraints = [
            models.UniqueConstraint(fields=["branch", "name"], name="uniq_warehouse_name_per_branch"),
        ]

    def __str__(self):
        return f"{self.branch} / {self.name}"


class StockLevel(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="stock_levels")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="stock_levels")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True, related_name="stock_levels")
    batch = models.ForeignKey(ProductBatch, on_delete=models.PROTECT, null=True, blank=True, related_name="stock_levels")
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["warehouse", "product", "variant", "batch"],
                name="uniq_stock_level_full_key",
                nulls_distinct=False,
            ),
            models.CheckConstraint(check=models.Q(quantity__gte=0), name="stock_level_quantity_non_negative"),
            models.CheckConstraint(check=models.Q(reserved_quantity__gte=0), name="stock_level_reserved_non_negative"),
        ]
        indexes = [
            models.Index(fields=["warehouse", "product"]),
            models.Index(fields=["product", "variant"]),
            models.Index(fields=["batch"]),
        ]

    @property
    def available_quantity(self):
        return self.quantity - self.reserved_quantity

    def clean(self):
        if self.variant and self.variant.product_id != self.product_id:
            raise ValidationError("Variant must belong to the selected product.")
        if self.batch and self.batch.product_id != self.product_id:
            raise ValidationError("Batch must belong to the selected product.")
        if self.batch and self.batch.variant_id and self.batch.variant_id != self.variant_id:
            raise ValidationError("Batch variant must match the selected variant.")
        if self.reserved_quantity > self.quantity:
            raise ValidationError("Reserved quantity cannot exceed physical quantity.")

    def __str__(self):
        return f"{self.warehouse}: {self.product} = {self.quantity}"


class StockMovement(CreatedByModel):
    class MovementType(models.TextChoices):
        IN = "IN", "Receipt"
        OUT = "OUT", "Write-off"
        SALE = "SALE", "Sale"
        RETURN = "RETURN", "Return"
        INVENTORY = "INVENTORY", "Inventory correction"
        TRANSFER = "TRANSFER", "Transfer"

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="stock_movements")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True, related_name="stock_movements")
    batch = models.ForeignKey(ProductBatch, on_delete=models.PROTECT, null=True, blank=True, related_name="stock_movements")
    source_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True, related_name="outgoing_movements")
    destination_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, null=True, blank=True, related_name="incoming_movements")
    movement_type = models.CharField(max_length=32, choices=MovementType.choices)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive.")
        if self.variant and self.variant.product_id != self.product_id:
            raise ValidationError("Variant must belong to the selected product.")
        if self.batch and self.batch.product_id != self.product_id:
            raise ValidationError("Batch must belong to the selected product.")

        if self.movement_type in {self.MovementType.OUT, self.MovementType.SALE} and not self.source_warehouse_id:
            raise ValidationError("Source warehouse is required for stock decrease.")
        if self.movement_type in {self.MovementType.IN, self.MovementType.RETURN, self.MovementType.INVENTORY} and not self.destination_warehouse_id:
            raise ValidationError("Destination warehouse is required for stock increase or inventory correction.")
        if self.movement_type == self.MovementType.TRANSFER:
            if not self.source_warehouse_id or not self.destination_warehouse_id:
                raise ValidationError("Transfer requires source and destination warehouses.")
            if self.source_warehouse_id == self.destination_warehouse_id:
                raise ValidationError("Transfer warehouses must be different.")

    def save(self, *args, **kwargs):
        if getattr(self, "_skip_stock_apply", False):
            return super().save(*args, **kwargs)
        from .services import apply_stock_movement

        return apply_stock_movement(self)

    def __str__(self):
        return f"{self.product} {self.movement_type} {self.quantity}"

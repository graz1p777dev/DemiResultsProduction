from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from common.models import CreatedByModel


class Category(CreatedByModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Brand(CreatedByModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(CreatedByModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=64, unique=True)
    barcode = models.CharField(max_length=64, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    ingredients = models.TextField(blank=True)
    usage_instructions = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0"))])
    stock_quantity = models.IntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["barcode"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold


class ProductVariant(CreatedByModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=64, unique=True)
    barcode = models.CharField(max_length=64, unique=True, blank=True, null=True)
    size = models.CharField(max_length=64, blank=True)
    color = models.CharField(max_length=64, blank=True)
    retail_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0"))])
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["product", "name"], name="uniq_variant_name_per_product"),
        ]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["barcode"]),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductBatch(CreatedByModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="batches")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True, related_name="batches")
    batch_number = models.CharField(max_length=128)
    expires_at = models.DateField(null=True, blank=True)
    received_at = models.DateField(null=True, blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0"))])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "variant", "batch_number"],
                name="uniq_batch_per_product_variant",
            ),
            models.UniqueConstraint(
                fields=["product", "batch_number"],
                condition=Q(variant__isnull=True),
                name="uniq_batch_per_product_without_variant",
            ),
        ]
        indexes = [
            models.Index(fields=["batch_number"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.product} batch {self.batch_number}"


class ProductImage(CreatedByModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product}"

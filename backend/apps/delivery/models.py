from django.conf import settings
from django.db import models

from apps.orders.models import Order
from common.models import CreatedByModel


class Address(CreatedByModel):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    city = models.CharField(max_length=128)
    street = models.CharField(max_length=255)
    house = models.CharField(max_length=64)
    apartment = models.CharField(max_length=64, blank=True)
    comment = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.city}, {self.street}, {self.house}"


class DeliveryZone(CreatedByModel):
    name = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Delivery(CreatedByModel):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        ASSIGNED = "ASSIGNED", "Assigned"
        DELIVERING = "DELIVERING", "Delivering"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="delivery")
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="deliveries")
    zone = models.ForeignKey(DeliveryZone, on_delete=models.PROTECT, related_name="deliveries")
    courier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="deliveries")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.CREATED)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Delivery for order {self.order_id}"


from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        CASHIER = "CASHIER", "Cashier"
        WAREHOUSE = "WAREHOUSE", "Warehouse"
        CLIENT = "CLIENT", "Client"
        AI_ASSISTANT = "AI_ASSISTANT", "AI Assistant"

    role = models.CharField(max_length=32, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField(max_length=32, blank=True)
    is_2fa_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")
    birth_date = models.DateField(null=True, blank=True)
    skin_type = models.CharField(max_length=128, blank=True)
    allergies = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Client profile: {self.user}"


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")
    position = models.CharField(max_length=128, blank=True)
    hired_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Staff profile: {self.user}"


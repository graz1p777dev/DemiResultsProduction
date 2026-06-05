from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from common.validators import kyrgyz_phone_validator


class User(AbstractUser):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        MANAGER = "MANAGER", "Manager"
        CASHIER = "CASHIER", "Cashier"
        WAREHOUSE = "WAREHOUSE", "Warehouse"
        CLIENT = "CLIENT", "Client"
        AI_ASSISTANT = "AI_ASSISTANT", "AI Assistant"

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=13, unique=True, null=True, blank=True, validators=[kyrgyz_phone_validator])
    google_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.CLIENT)
    is_2fa_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client_profile")

    # Personal
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=32, blank=True)

    # Skin card
    skin_type = models.CharField(max_length=64, blank=True)
    skin_concerns = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    complaints = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    current_routine = models.TextField(blank=True)
    previous_treatments = models.TextField(blank=True)

    # AI / consultation
    ai_summary = models.TextField(blank=True)
    telegram_username = models.CharField(max_length=128, blank=True, db_index=True)
    # external_ai_id is intentionally not active now. Add it later if AI providers need stable external IDs.
    recommendations = models.TextField(blank=True)
    staff_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    # Stats
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Client profile: {self.user}"


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")
    position = models.CharField(max_length=128, blank=True)
    hired_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Staff profile: {self.user}"


class PhoneAuthCode(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = "LOGIN", "Login"

    phone = models.CharField(max_length=13, validators=[kyrgyz_phone_validator], db_index=True)
    code_hash = models.CharField(max_length=128)
    purpose = models.CharField(max_length=32, choices=Purpose.choices, default=Purpose.LOGIN)
    attempts = models.PositiveSmallIntegerField(default=0)
    max_attempts = models.PositiveSmallIntegerField(default=5)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=["phone", "purpose", "consumed_at"]),
            models.Index(fields=["expires_at"]),
        ]

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def is_consumed(self):
        return self.consumed_at is not None

    def __str__(self):
        return f"{self.phone} {self.purpose}"

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ClientProfile, PhoneAuthCode, StaffProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("DemiResults", {"fields": ("role", "phone", "google_id", "is_2fa_enabled")}),
    )
    list_display = ("username", "email", "phone", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")


admin.site.register(ClientProfile)
admin.site.register(StaffProfile)


@admin.register(PhoneAuthCode)
class PhoneAuthCodeAdmin(admin.ModelAdmin):
    list_display = ("phone", "purpose", "attempts", "expires_at", "consumed_at", "created_at")
    list_filter = ("purpose", "consumed_at")
    search_fields = ("phone",)
    readonly_fields = ("code_hash", "created_at")

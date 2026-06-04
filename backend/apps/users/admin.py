from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ClientProfile, StaffProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("DemiResults", {"fields": ("role", "phone", "is_2fa_enabled")}),
    )
    list_display = ("username", "email", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")


admin.site.register(ClientProfile)
admin.site.register(StaffProfile)


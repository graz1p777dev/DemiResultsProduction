from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "channel", "title", "is_read", "sent_at")
    list_filter = ("channel", "is_read", "sent_at")
    search_fields = ("title", "body", "provider_reference", "user__phone", "user__email")

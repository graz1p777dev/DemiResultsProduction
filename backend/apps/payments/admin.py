from django.contrib import admin

from .models import Payment, PaymentRefund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "method", "status", "provider", "provider_reference", "amount", "paid_at"]
    list_filter = ["method", "status", "provider"]
    search_fields = ["provider_reference", "external_id"]


admin.site.register(PaymentRefund)

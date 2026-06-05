from django.contrib import admin

from .models import Sale, SaleItem, SaleReturn


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "cashier", "client", "warehouse", "status", "total", "profit", "created_at")
    list_filter = ("status", "warehouse", "created_at")
    search_fields = ("id", "cashier__username", "client__username")


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("sale", "product", "variant", "batch", "quantity", "unit_price", "unit_cost")
    list_filter = ("product", "variant")


@admin.register(SaleReturn)
class SaleReturnAdmin(admin.ModelAdmin):
    list_display = ("sale", "total_refund", "created_by", "created_at")

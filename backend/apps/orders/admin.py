from django.contrib import admin

from .models import Order, OrderItem, OrderStatusHistory


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "warehouse", "status", "total", "created_at")
    list_filter = ("status", "warehouse", "created_at")
    search_fields = ("id", "client__username", "client__phone")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "variant", "batch", "quantity", "unit_price")


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "from_status", "to_status", "created_by", "created_at")
    list_filter = ("to_status", "created_at")

from django.contrib import admin

from .models import Branch, StockLevel, StockMovement, Warehouse


admin.site.register(Branch)
admin.site.register(Warehouse)
admin.site.register(StockLevel)
admin.site.register(StockMovement)

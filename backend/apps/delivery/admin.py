from django.contrib import admin

from .models import Address, Delivery, DeliveryZone


admin.site.register(Address)
admin.site.register(DeliveryZone)
admin.site.register(Delivery)


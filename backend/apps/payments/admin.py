from django.contrib import admin

from .models import Payment, PaymentRefund


admin.site.register(Payment)
admin.site.register(PaymentRefund)


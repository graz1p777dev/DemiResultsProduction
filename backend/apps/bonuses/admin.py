from django.contrib import admin

from .models import BonusAccount, BonusTransaction, PromoCode


admin.site.register(BonusAccount)
admin.site.register(BonusTransaction)
admin.site.register(PromoCode)


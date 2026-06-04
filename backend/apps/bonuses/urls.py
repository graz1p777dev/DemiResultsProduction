from rest_framework.routers import DefaultRouter

from .views import BonusAccountViewSet, BonusTransactionViewSet, PromoCodeViewSet

router = DefaultRouter()
router.register("accounts", BonusAccountViewSet)
router.register("transactions", BonusTransactionViewSet)
router.register("promo-codes", PromoCodeViewSet)

urlpatterns = router.urls


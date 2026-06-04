from rest_framework.routers import DefaultRouter

from .views import PaymentRefundViewSet, PaymentViewSet

router = DefaultRouter()
router.register("payments", PaymentViewSet)
router.register("refunds", PaymentRefundViewSet)

urlpatterns = router.urls


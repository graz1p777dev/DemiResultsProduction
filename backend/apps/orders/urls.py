from rest_framework.routers import DefaultRouter

from .views import OrderItemViewSet, OrderStatusHistoryViewSet, OrderViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet)
router.register("order-items", OrderItemViewSet)
router.register("status-history", OrderStatusHistoryViewSet)

urlpatterns = router.urls

from rest_framework.routers import DefaultRouter

from .views import OrderItemViewSet, OrderViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet)
router.register("order-items", OrderItemViewSet)

urlpatterns = router.urls


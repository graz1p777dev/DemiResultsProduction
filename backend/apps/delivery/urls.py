from rest_framework.routers import DefaultRouter

from .views import AddressViewSet, DeliveryViewSet, DeliveryZoneViewSet

router = DefaultRouter()
router.register("addresses", AddressViewSet)
router.register("zones", DeliveryZoneViewSet)
router.register("deliveries", DeliveryViewSet)

urlpatterns = router.urls


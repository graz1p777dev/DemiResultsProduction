from rest_framework.routers import DefaultRouter

from .views import SaleItemViewSet, SaleReturnViewSet, SaleViewSet

router = DefaultRouter()
router.register("sales", SaleViewSet)
router.register("sale-items", SaleItemViewSet)
router.register("returns", SaleReturnViewSet)

urlpatterns = router.urls


from rest_framework.routers import DefaultRouter

from .views import BranchViewSet, StockLevelViewSet, StockMovementViewSet, WarehouseViewSet

router = DefaultRouter()
router.register("branches", BranchViewSet)
router.register("warehouses", WarehouseViewSet)
router.register("stock-levels", StockLevelViewSet)
router.register("stock-movements", StockMovementViewSet)

urlpatterns = router.urls

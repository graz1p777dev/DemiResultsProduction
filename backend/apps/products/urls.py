from rest_framework.routers import DefaultRouter

from .views import (
    BrandViewSet,
    CategoryViewSet,
    ProductBatchViewSet,
    ProductImageViewSet,
    ProductVariantViewSet,
    ProductViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("brands", BrandViewSet)
router.register("products", ProductViewSet)
router.register("variants", ProductVariantViewSet)
router.register("batches", ProductBatchViewSet)
router.register("images", ProductImageViewSet)

urlpatterns = router.urls

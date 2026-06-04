from rest_framework.routers import DefaultRouter

from .views import BrandViewSet, CategoryViewSet, ProductImageViewSet, ProductViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("brands", BrandViewSet)
router.register("products", ProductViewSet)
router.register("images", ProductImageViewSet)

urlpatterns = router.urls


from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CatalogBrandViewSet,
    CatalogCategoryViewSet,
    CatalogProductViewSet,
    MeView,
    MyBonusView,
    MyConsultationViewSet,
    MyOrderViewSet,
)

catalog_router = DefaultRouter()
catalog_router.register("categories", CatalogCategoryViewSet, basename="catalog-categories")
catalog_router.register("brands", CatalogBrandViewSet, basename="catalog-brands")
catalog_router.register("products", CatalogProductViewSet, basename="catalog-products")

me_router = DefaultRouter()
me_router.register("orders", MyOrderViewSet, basename="me-orders")
me_router.register("consultations", MyConsultationViewSet, basename="me-consultations")

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("me/bonuses/", MyBonusView.as_view(), name="me-bonuses"),
    path("me/", include(me_router.urls)),
    path("catalog/", include(catalog_router.urls)),
]

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ReportExportViewSet,
    bonuses_report,
    inventory_report,
    orders_report,
    sales_report,
)

router = DefaultRouter()
router.register("exports", ReportExportViewSet)

urlpatterns = [
    path("sales.xlsx", sales_report, name="sales-report"),
    path("inventory.xlsx", inventory_report, name="inventory-report"),
    path("orders.xlsx", orders_report, name="orders-report"),
    path("bonuses.xlsx", bonuses_report, name="bonuses-report"),
] + router.urls


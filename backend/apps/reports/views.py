from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from openpyxl import Workbook
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes

from apps.bonuses.models import BonusAccount
from apps.orders.models import Order
from apps.products.models import Product
from apps.sales.models import Sale
from common.permissions import IsOwnerAdminManager
from common.views import CreatedByModelViewSet

from .models import ReportExport
from .serializers import ReportExportSerializer


def workbook_response(workbook, filename):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response


class ReportExportViewSet(CreatedByModelViewSet):
    queryset = ReportExport.objects.all().order_by("-created_at")
    serializer_class = ReportExportSerializer
    permission_classes = [IsOwnerAdminManager]


@extend_schema(responses={(200, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"): OpenApiTypes.BINARY})
@api_view(["GET"])
@permission_classes([IsOwnerAdminManager])
def sales_report(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sales"
    sheet.append(["ID", "Cashier", "Client", "Status", "Subtotal", "Discount", "Bonus spent", "Total", "Created"])
    for sale in Sale.objects.select_related("cashier", "client").order_by("-created_at"):
        sheet.append([
            sale.id,
            sale.cashier.username,
            sale.client.username if sale.client else "",
            sale.status,
            sale.subtotal,
            sale.discount_total,
            sale.bonus_spent,
            sale.total,
            sale.created_at.isoformat(),
        ])
    return workbook_response(workbook, "sales_report.xlsx")


@extend_schema(responses={(200, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"): OpenApiTypes.BINARY})
@api_view(["GET"])
@permission_classes([IsOwnerAdminManager])
def inventory_report(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Inventory"
    sheet.append(["ID", "SKU", "Name", "Brand", "Category", "Stock", "Low threshold", "Price"])
    for product in Product.objects.select_related("brand", "category").order_by("name"):
        sheet.append([
            product.id,
            product.sku,
            product.name,
            product.brand.name,
            product.category.name,
            product.stock_quantity,
            product.low_stock_threshold,
            product.price,
        ])
    return workbook_response(workbook, "inventory_report.xlsx")


@extend_schema(responses={(200, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"): OpenApiTypes.BINARY})
@api_view(["GET"])
@permission_classes([IsOwnerAdminManager])
def orders_report(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Orders"
    sheet.append(["ID", "Client", "Status", "Subtotal", "Delivery", "Discount", "Total", "Created"])
    for order in Order.objects.select_related("client").order_by("-created_at"):
        sheet.append([
            order.id,
            order.client.username,
            order.status,
            order.subtotal,
            order.delivery_price,
            order.discount_total,
            order.total,
            order.created_at.isoformat(),
        ])
    return workbook_response(workbook, "orders_report.xlsx")


@extend_schema(responses={(200, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"): OpenApiTypes.BINARY})
@api_view(["GET"])
@permission_classes([IsOwnerAdminManager])
def bonuses_report(request):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Bonuses"
    sheet.append(["Client", "Balance", "Updated"])
    for account in BonusAccount.objects.select_related("client").order_by("client__username"):
        sheet.append([account.client.username, account.balance, account.updated_at.isoformat()])
    return workbook_response(workbook, "bonuses_report.xlsx")

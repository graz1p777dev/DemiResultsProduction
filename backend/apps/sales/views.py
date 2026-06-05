from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import IsSalesOperator
from common.views import CreatedByModelViewSet

from .models import Sale, SaleItem, SaleReturn
from .serializers import SaleItemSerializer, SaleReturnSerializer, SaleSerializer
from . import services


@extend_schema_view(
    list=extend_schema(tags=["Sales"], description="List POS sales with totals, cost and profit."),
    create=extend_schema(
        tags=["Sales"],
        description="Create a POS sale header. Add items through /api/sales/sale-items/ to write off stock.",
        examples=[
            OpenApiExample("Create sale", value={"warehouse": 1, "client": 2, "discount_total": "0.00", "bonus_spent": "0.00"}, request_only=True),
        ],
    ),
)
class SaleViewSet(CreatedByModelViewSet):
    queryset = Sale.objects.select_related("cashier", "client", "warehouse").prefetch_related("items").all()
    serializer_class = SaleSerializer
    permission_classes = [IsSalesOperator]
    filterset_fields = ["status", "cashier", "client", "warehouse"]
    ordering_fields = ["created_at", "total", "profit"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, cashier=self.request.user)

    @extend_schema(tags=["Sales"], description="Complete sale and optionally accrue bonuses for the client.")
    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        sale = services.complete_sale(self.get_object())
        return Response(self.get_serializer(sale).data)

    @extend_schema(tags=["Sales"], description="Refund sale once and restore stock.")
    @action(detail=True, methods=["post"])
    def refund(self, request, pk=None):
        refund = services.refund_sale(sale=self.get_object(), created_by=request.user, reason=request.data.get("reason", ""))
        return Response(SaleReturnSerializer(refund).data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    create=extend_schema(
        tags=["Sales"],
        description="Add an item to a sale. The backend fixes retail price/cost and writes off stock through inventory services.",
        examples=[
            OpenApiExample("Add sale item", value={"sale": 1, "product": 1, "quantity": 2}, request_only=True),
        ],
    ),
    list=extend_schema(tags=["Sales"]),
)
class SaleItemViewSet(CreatedByModelViewSet):
    queryset = SaleItem.objects.select_related("sale", "product", "variant", "batch").all()
    serializer_class = SaleItemSerializer
    permission_classes = [IsSalesOperator]
    filterset_fields = ["sale", "product", "variant", "batch"]

    def perform_create(self, serializer):
        serializer.instance = services.add_sale_item(**serializer.validated_data)


@extend_schema_view(
    create=extend_schema(
        tags=["Sales"],
        description="Refund a sale once. The backend restores stock through inventory services and prevents duplicate returns.",
        examples=[OpenApiExample("Refund sale", value={"sale": 1, "reason": "Client return"}, request_only=True)],
    ),
    list=extend_schema(tags=["Sales"]),
)
class SaleReturnViewSet(CreatedByModelViewSet):
    queryset = SaleReturn.objects.select_related("sale", "created_by").all()
    serializer_class = SaleReturnSerializer
    permission_classes = [IsSalesOperator]

    def perform_create(self, serializer):
        serializer.instance = services.refund_sale(
            sale=serializer.validated_data["sale"],
            reason=serializer.validated_data.get("reason", ""),
            created_by=self.request.user,
        )

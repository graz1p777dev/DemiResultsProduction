from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import IsInventoryOperator
from common.views import CreatedByModelViewSet

from . import services
from .models import Branch, StockLevel, StockMovement, Warehouse
from .serializers import BranchSerializer, StockLevelSerializer, StockMovementSerializer, WarehouseSerializer


class BranchViewSet(CreatedByModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsInventoryOperator]
    search_fields = ["name", "code", "address"]


class WarehouseViewSet(CreatedByModelViewSet):
    queryset = Warehouse.objects.select_related("branch").all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsInventoryOperator]
    filterset_fields = ["branch", "is_active"]
    search_fields = ["name", "code", "branch__name"]


class StockLevelViewSet(CreatedByModelViewSet):
    queryset = StockLevel.objects.select_related("warehouse", "product", "variant", "batch").all()
    serializer_class = StockLevelSerializer
    permission_classes = [IsInventoryOperator]
    filterset_fields = ["warehouse", "product", "variant", "batch"]
    search_fields = ["product__name", "product__sku", "variant__sku", "batch__batch_number"]


@extend_schema_view(
    list=extend_schema(tags=["Inventory"], description="List stock movements with product, warehouse, movement type and date filters."),
    create=extend_schema(
        tags=["Inventory"],
        description="Create a stock movement. This is the only API path that changes physical stock.",
        examples=[
            OpenApiExample(
                "Receipt",
                value={"product": 1, "destination_warehouse": 1, "movement_type": "IN", "quantity": 10, "reason": "Supplier receipt"},
                request_only=True,
            ),
            OpenApiExample(
                "Transfer",
                value={"product": 1, "source_warehouse": 1, "destination_warehouse": 2, "movement_type": "TRANSFER", "quantity": 3},
                request_only=True,
            ),
        ],
    ),
)
class StockMovementViewSet(CreatedByModelViewSet):
    queryset = StockMovement.objects.select_related(
        "product", "variant", "batch", "source_warehouse", "destination_warehouse", "created_by"
    ).all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsInventoryOperator]
    filterset_fields = ["product", "variant", "batch", "movement_type", "source_warehouse", "destination_warehouse"]
    search_fields = ["reason", "reference", "product__name", "product__sku", "variant__sku"]
    ordering_fields = ["created_at", "quantity"]

    @extend_schema(tags=["Inventory"], description="Receive stock into a warehouse.")
    @action(detail=False, methods=["post"], url_path="receive")
    def receive(self, request):
        serializer = self.get_serializer(data={**request.data, "movement_type": StockMovement.MovementType.IN})
        serializer.is_valid(raise_exception=True)
        movement = services.receive_stock(
            product=serializer.validated_data["product"],
            variant=serializer.validated_data.get("variant"),
            batch=serializer.validated_data.get("batch"),
            warehouse=serializer.validated_data["destination_warehouse"],
            quantity=serializer.validated_data["quantity"],
            reason=serializer.validated_data.get("reason", "Stock receipt"),
            reference=serializer.validated_data.get("reference", ""),
            created_by=request.user,
        )
        return Response(self.get_serializer(movement).data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["Inventory"], description="Write off stock from a warehouse.")
    @action(detail=False, methods=["post"], url_path="write-off")
    def write_off(self, request):
        serializer = self.get_serializer(data={**request.data, "movement_type": StockMovement.MovementType.OUT})
        serializer.is_valid(raise_exception=True)
        movement = services.write_off_stock(
            product=serializer.validated_data["product"],
            variant=serializer.validated_data.get("variant"),
            batch=serializer.validated_data.get("batch"),
            warehouse=serializer.validated_data["source_warehouse"],
            quantity=serializer.validated_data["quantity"],
            reason=serializer.validated_data.get("reason", "Stock write-off"),
            reference=serializer.validated_data.get("reference", ""),
            created_by=request.user,
        )
        return Response(self.get_serializer(movement).data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["Inventory"], description="Transfer stock between warehouses.")
    @action(detail=False, methods=["post"], url_path="transfer")
    def transfer(self, request):
        serializer = self.get_serializer(data={**request.data, "movement_type": StockMovement.MovementType.TRANSFER})
        serializer.is_valid(raise_exception=True)
        movement = services.move_stock(
            product=serializer.validated_data["product"],
            variant=serializer.validated_data.get("variant"),
            batch=serializer.validated_data.get("batch"),
            source_warehouse=serializer.validated_data["source_warehouse"],
            destination_warehouse=serializer.validated_data["destination_warehouse"],
            quantity=serializer.validated_data["quantity"],
            reason=serializer.validated_data.get("reason", "Stock transfer"),
            reference=serializer.validated_data.get("reference", ""),
            created_by=request.user,
        )
        return Response(self.get_serializer(movement).data, status=status.HTTP_201_CREATED)

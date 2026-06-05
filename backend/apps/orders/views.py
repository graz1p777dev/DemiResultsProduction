from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from common.views import CreatedByModelViewSet

from .models import Order, OrderItem, OrderStatusHistory
from .serializers import OrderItemSerializer, OrderSerializer, OrderStatusHistorySerializer
from . import services


@extend_schema_view(
    list=extend_schema(tags=["Orders"], description="List customer orders. Clients only see their own orders."),
    create=extend_schema(
        tags=["Orders"],
        description="Create an order header. Add products through /api/orders/order-items/.",
        examples=[OpenApiExample("Create order", value={"client": 1, "warehouse": 1, "delivery_price": "150.00", "comment": "Call before delivery"}, request_only=True)],
    ),
    update=extend_schema(tags=["Orders"], description="Update an order. Status changes are validated by allowed backend transitions."),
    partial_update=extend_schema(tags=["Orders"], description="Patch an order. Status changes write OrderStatusHistory."),
)
class OrderViewSet(CreatedByModelViewSet):
    queryset = Order.objects.select_related("client", "warehouse").prefetch_related("items", "status_history").all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "client", "warehouse"]
    ordering_fields = ["created_at", "total"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.role in {"OWNER", "ADMIN", "MANAGER", "CASHIER", "WAREHOUSE"}:
            return queryset
        return queryset.filter(client=self.request.user)

    def perform_update(self, serializer):
        old_status = serializer.instance.status
        if "status" in serializer.validated_data and serializer.validated_data["status"] != old_status:
            serializer.instance = services.change_order_status(
                order=serializer.instance,
                to_status=serializer.validated_data["status"],
                created_by=self.request.user,
            )
            for field, value in serializer.validated_data.items():
                if field != "status":
                    setattr(serializer.instance, field, value)
            if any(field != "status" for field in serializer.validated_data):
                serializer.instance.save()
            return
        order = serializer.save()
        if old_status != order.status:
            services.create_order_status_history(
                order=order,
                from_status=old_status,
                to_status=order.status,
                created_by=self.request.user,
            )

    @extend_schema(tags=["Orders"], description="Cancel an order before PACKING. Releases reserved stock if needed.")
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = services.cancel_order(order=self.get_object(), created_by=request.user, comment=request.data.get("comment", ""))
        return Response(self.get_serializer(order).data)

    @extend_schema(tags=["Orders"], description="Change order status using backend-validated transitions.")
    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, pk=None):
        order = services.change_order_status(
            order=self.get_object(),
            to_status=request.data.get("status"),
            created_by=request.user,
            comment=request.data.get("comment", ""),
        )
        return Response(self.get_serializer(order).data)


@extend_schema_view(
    create=extend_schema(
        tags=["Orders"],
        description="Add a product to an order before PACKING. Price is fixed by backend.",
        examples=[OpenApiExample("Add order item", value={"order": 1, "product": 1, "quantity": 1}, request_only=True)],
    ),
    list=extend_schema(tags=["Orders"]),
)
class OrderItemViewSet(CreatedByModelViewSet):
    queryset = OrderItem.objects.select_related("order", "product", "variant", "batch").all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["order", "product", "variant", "batch"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.role in {"OWNER", "ADMIN", "MANAGER", "CASHIER", "WAREHOUSE"}:
            return queryset
        return queryset.filter(order__client=self.request.user)

    def perform_create(self, serializer):
        serializer.instance = services.add_order_item(**serializer.validated_data)


@extend_schema_view(list=extend_schema(tags=["Orders"], description="Order status transition history."))
class OrderStatusHistoryViewSet(CreatedByModelViewSet):
    queryset = OrderStatusHistory.objects.select_related("order", "created_by").all()
    serializer_class = OrderStatusHistorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["order", "from_status", "to_status"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.role in {"OWNER", "ADMIN", "MANAGER", "CASHIER", "WAREHOUSE"}:
            return queryset
        return queryset.filter(order__client=self.request.user)

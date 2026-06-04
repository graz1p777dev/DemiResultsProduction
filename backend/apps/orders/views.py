from rest_framework.permissions import IsAuthenticated

from common.views import CreatedByModelViewSet

from .models import Order, OrderItem
from .serializers import OrderItemSerializer, OrderSerializer


class OrderViewSet(CreatedByModelViewSet):
    queryset = Order.objects.select_related("client").prefetch_related("items").all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "client"]
    ordering_fields = ["created_at", "total"]


class OrderItemViewSet(CreatedByModelViewSet):
    queryset = OrderItem.objects.select_related("order", "product").all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["order", "product"]


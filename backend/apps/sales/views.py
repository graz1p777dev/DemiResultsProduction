from common.permissions import IsStaffOperator
from common.views import CreatedByModelViewSet

from .models import Sale, SaleItem, SaleReturn
from .serializers import SaleItemSerializer, SaleReturnSerializer, SaleSerializer


class SaleViewSet(CreatedByModelViewSet):
    queryset = Sale.objects.select_related("cashier", "client").prefetch_related("items").all()
    serializer_class = SaleSerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["status", "cashier", "client"]
    ordering_fields = ["created_at", "total"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, cashier=self.request.user)


class SaleItemViewSet(CreatedByModelViewSet):
    queryset = SaleItem.objects.select_related("sale", "product").all()
    serializer_class = SaleItemSerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["sale", "product"]


class SaleReturnViewSet(CreatedByModelViewSet):
    queryset = SaleReturn.objects.select_related("sale", "created_by").all()
    serializer_class = SaleReturnSerializer
    permission_classes = [IsStaffOperator]

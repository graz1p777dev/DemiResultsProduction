from common.permissions import IsStaffOperator
from common.views import CreatedByModelViewSet

from .models import StockMovement
from .serializers import StockMovementSerializer


class StockMovementViewSet(CreatedByModelViewSet):
    queryset = StockMovement.objects.select_related("product", "created_by").all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["product", "movement_type"]
    search_fields = ["reason", "reference", "product__name", "product__sku"]
    ordering_fields = ["created_at", "quantity"]


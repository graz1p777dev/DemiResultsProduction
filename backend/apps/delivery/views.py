from rest_framework.permissions import IsAuthenticated

from common.permissions import IsStaffOperator
from common.views import CreatedByModelViewSet

from .models import Address, Delivery, DeliveryZone
from .serializers import AddressSerializer, DeliverySerializer, DeliveryZoneSerializer


class AddressViewSet(CreatedByModelViewSet):
    queryset = Address.objects.select_related("client").all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["client", "city", "is_default"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.role in {"OWNER", "ADMIN", "MANAGER", "CASHIER"}:
            return queryset
        return queryset.filter(client=self.request.user)


class DeliveryZoneViewSet(CreatedByModelViewSet):
    queryset = DeliveryZone.objects.all()
    serializer_class = DeliveryZoneSerializer
    permission_classes = [IsStaffOperator]


class DeliveryViewSet(CreatedByModelViewSet):
    queryset = Delivery.objects.select_related("order", "address", "zone", "courier").all()
    serializer_class = DeliverySerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["status", "courier", "zone"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.role in {"OWNER", "ADMIN", "MANAGER", "CASHIER", "WAREHOUSE"}:
            return queryset
        return queryset.filter(order__client=self.request.user)

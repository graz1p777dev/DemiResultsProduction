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


class DeliveryZoneViewSet(CreatedByModelViewSet):
    queryset = DeliveryZone.objects.all()
    serializer_class = DeliveryZoneSerializer
    permission_classes = [IsStaffOperator]


class DeliveryViewSet(CreatedByModelViewSet):
    queryset = Delivery.objects.select_related("order", "address", "zone", "courier").all()
    serializer_class = DeliverySerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["status", "courier", "zone"]


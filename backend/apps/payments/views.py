from common.permissions import IsStaffOperator
from common.views import CreatedByModelViewSet

from .models import Payment, PaymentRefund
from .serializers import PaymentRefundSerializer, PaymentSerializer


class PaymentViewSet(CreatedByModelViewSet):
    queryset = Payment.objects.select_related("order", "sale").all()
    serializer_class = PaymentSerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["method", "status", "order", "sale"]


class PaymentRefundViewSet(CreatedByModelViewSet):
    queryset = PaymentRefund.objects.select_related("payment").all()
    serializer_class = PaymentRefundSerializer
    permission_classes = [IsStaffOperator]


from common.permissions import IsStaffOperator
from common.views import CreatedByModelViewSet

from .models import BonusAccount, BonusTransaction, PromoCode
from .serializers import BonusAccountSerializer, BonusTransactionSerializer, PromoCodeSerializer


class BonusAccountViewSet(CreatedByModelViewSet):
    queryset = BonusAccount.objects.select_related("client").all()
    serializer_class = BonusAccountSerializer
    permission_classes = [IsStaffOperator]


class BonusTransactionViewSet(CreatedByModelViewSet):
    queryset = BonusTransaction.objects.select_related("account", "created_by").all()
    serializer_class = BonusTransactionSerializer
    permission_classes = [IsStaffOperator]


class PromoCodeViewSet(CreatedByModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer
    permission_classes = [IsStaffOperator]
    search_fields = ["code"]


from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from common.permissions import IsStaffOperator
from common.views import CreatedByModelViewSet

from .models import BonusAccount, BonusTransaction, PromoCode
from .serializers import BonusAccountSerializer, BonusTransactionSerializer, PromoCodeSerializer


@extend_schema_view(list=extend_schema(tags=["Bonuses"], description="List client bonus accounts and balances."))
class BonusAccountViewSet(CreatedByModelViewSet):
    queryset = BonusAccount.objects.select_related("client").all()
    serializer_class = BonusAccountSerializer
    permission_classes = [IsStaffOperator]

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsStaffOperator()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.role in {"OWNER", "ADMIN", "MANAGER", "CASHIER"}:
            return queryset
        return queryset.filter(client=self.request.user)


@extend_schema_view(list=extend_schema(tags=["Bonuses"]), create=extend_schema(tags=["Bonuses"], description="Create a bonus transaction. Prefer bonuses.services for accrual/spend flows."))
class BonusTransactionViewSet(CreatedByModelViewSet):
    queryset = BonusTransaction.objects.select_related("account", "created_by").all()
    serializer_class = BonusTransactionSerializer
    permission_classes = [IsStaffOperator]

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsStaffOperator()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.role in {"OWNER", "ADMIN", "MANAGER", "CASHIER"}:
            return queryset
        return queryset.filter(account__client=self.request.user)


@extend_schema_view(list=extend_schema(tags=["Bonuses"]), create=extend_schema(tags=["Bonuses"]))
class PromoCodeViewSet(CreatedByModelViewSet):
    queryset = PromoCode.objects.all()
    serializer_class = PromoCodeSerializer
    permission_classes = [IsStaffOperator]
    search_fields = ["code"]

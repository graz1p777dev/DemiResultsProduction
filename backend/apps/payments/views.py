from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.orders.models import Order
from apps.sales.models import Sale
from common.permissions import IsStaffOperator
from common.views import CreatedByModelViewSet

from . import services
from .models import Payment, PaymentRefund
from .serializers import LocalPaymentCreateSerializer, LocalPaymentFailureSerializer, PaymentRefundSerializer, PaymentSerializer


class PaymentViewSet(CreatedByModelViewSet):
    queryset = Payment.objects.select_related("order", "sale").all()
    serializer_class = PaymentSerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["method", "status", "order", "sale"]

    def perform_create(self, serializer):
        serializer.instance = services.create_payment(created_by=self.request.user, **serializer.validated_data)

    @extend_schema(
        tags=["Payments"],
        request=LocalPaymentCreateSerializer,
        responses={201: PaymentSerializer},
        description="Create a local development online payment. No card/bank data is accepted or stored.",
    )
    @action(detail=False, methods=["post"], url_path="local")
    def create_local(self, request):
        serializer = LocalPaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = get_object_or_404(Order, pk=serializer.validated_data["order"]) if serializer.validated_data.get("order") else None
        sale = get_object_or_404(Sale, pk=serializer.validated_data["sale"]) if serializer.validated_data.get("sale") else None
        payment = services.create_local_payment(
            amount=serializer.validated_data["amount"],
            order=order,
            sale=sale,
            created_by=request.user,
        )
        return Response(self.get_serializer(payment).data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["Payments"], description="Mark a pending/failed payment as paid.")
    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        payment = services.mark_payment_paid(payment=self.get_object(), created_by=request.user, external_id=request.data.get("external_id", ""))
        return Response(self.get_serializer(payment).data)

    @extend_schema(tags=["Payments"], description="Confirm a local development payment as paid.")
    @action(detail=True, methods=["post"], url_path="confirm-local")
    def confirm_local(self, request, pk=None):
        payment = self.get_object()
        if payment.provider != "local":
            return Response({"detail": "Only local provider payments can be confirmed here."}, status=400)
        payment = services.mark_payment_paid(payment=payment, created_by=request.user, external_id=payment.provider_reference)
        return Response(self.get_serializer(payment).data)

    @extend_schema(tags=["Payments"], request=LocalPaymentFailureSerializer, description="Fail a pending local development payment.")
    @action(detail=True, methods=["post"], url_path="fail-local")
    def fail_local(self, request, pk=None):
        serializer = LocalPaymentFailureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = services.fail_local_payment(payment=self.get_object(), created_by=request.user, reason=serializer.validated_data.get("reason", ""))
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(self.get_serializer(payment).data)

    @extend_schema(tags=["Payments"], description="Refund a paid payment.")
    @action(detail=True, methods=["post"])
    def refund(self, request, pk=None):
        refund = services.refund_payment(
            payment=self.get_object(),
            amount=request.data.get("amount"),
            reason=request.data.get("reason", ""),
            created_by=request.user,
        )
        return Response(PaymentRefundSerializer(refund).data, status=status.HTTP_201_CREATED)


class PaymentRefundViewSet(CreatedByModelViewSet):
    queryset = PaymentRefund.objects.select_related("payment").all()
    serializer_class = PaymentRefundSerializer
    permission_classes = [IsStaffOperator]

    def perform_create(self, serializer):
        serializer.instance = services.refund_payment(created_by=self.request.user, **serializer.validated_data)

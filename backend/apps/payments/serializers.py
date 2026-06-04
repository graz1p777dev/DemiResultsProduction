from rest_framework import serializers

from .models import Payment, PaymentRefund


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at"]


class PaymentRefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRefund
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at"]


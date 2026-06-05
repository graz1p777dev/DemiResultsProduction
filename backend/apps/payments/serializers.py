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


class LocalPaymentCreateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    order = serializers.IntegerField(required=False)
    sale = serializers.IntegerField(required=False)

    def validate(self, attrs):
        if not attrs.get("order") and not attrs.get("sale"):
            raise serializers.ValidationError("order or sale is required.")
        if attrs.get("order") and attrs.get("sale"):
            raise serializers.ValidationError("Only one of order or sale can be provided.")
        return attrs


class LocalPaymentFailureSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)

from rest_framework import serializers

from .models import Sale, SaleItem, SaleReturn


class SaleItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    cost_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = SaleItem
        fields = "__all__"
        read_only_fields = ["unit_price", "unit_cost"]


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "created_at",
            "updated_at",
            "cashier",
            "subtotal",
            "cost_total",
            "total",
            "profit",
            "completed_at",
        ]


class SaleReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleReturn
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at", "total_refund"]

from rest_framework import serializers

from .models import BonusAccount, BonusTransaction, PromoCode


class BonusAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusAccount
        fields = "__all__"


class BonusTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusTransaction
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at"]


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at"]


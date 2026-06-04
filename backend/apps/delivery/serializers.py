from rest_framework import serializers

from .models import Address, Delivery, DeliveryZone


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at"]


class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at"]


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at"]


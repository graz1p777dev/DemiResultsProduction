from rest_framework import serializers

from .models import Consultation, ConsultationMessage


class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at"]


class ConsultationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationMessage
        fields = "__all__"
        read_only_fields = ["created_by", "created_at", "updated_at"]


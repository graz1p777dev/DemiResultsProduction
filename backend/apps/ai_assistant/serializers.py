from rest_framework import serializers

from .models import AIConversation, AIMessage, AIWebhookLog


class AIConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConversation
        fields = "__all__"


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = "__all__"


class AIWebhookLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIWebhookLog
        fields = "__all__"


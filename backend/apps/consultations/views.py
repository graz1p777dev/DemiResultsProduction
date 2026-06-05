from rest_framework.permissions import IsAuthenticated

from common.views import CreatedByModelViewSet

from .models import Consultation, ConsultationMessage
from .serializers import ConsultationMessageSerializer, ConsultationSerializer


class ConsultationViewSet(CreatedByModelViewSet):
    queryset = Consultation.objects.select_related("client", "consultant").all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "client", "consultant"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.role in {"OWNER", "ADMIN", "MANAGER"}:
            return queryset
        return queryset.filter(client=self.request.user) | queryset.filter(consultant=self.request.user)


class ConsultationMessageViewSet(CreatedByModelViewSet):
    queryset = ConsultationMessage.objects.select_related("consultation", "sender").all()
    serializer_class = ConsultationMessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["consultation", "sender"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.role in {"OWNER", "ADMIN", "MANAGER"}:
            return queryset
        return queryset.filter(consultation__client=self.request.user) | queryset.filter(consultation__consultant=self.request.user)

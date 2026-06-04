from rest_framework.permissions import IsAuthenticated

from common.views import CreatedByModelViewSet

from .models import Consultation, ConsultationMessage
from .serializers import ConsultationMessageSerializer, ConsultationSerializer


class ConsultationViewSet(CreatedByModelViewSet):
    queryset = Consultation.objects.select_related("client", "consultant").all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "client", "consultant"]


class ConsultationMessageViewSet(CreatedByModelViewSet):
    queryset = ConsultationMessage.objects.select_related("consultation", "sender").all()
    serializer_class = ConsultationMessageSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["consultation", "sender"]


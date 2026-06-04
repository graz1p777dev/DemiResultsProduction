from rest_framework.permissions import IsAuthenticated

from common.views import CreatedByModelViewSet

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(CreatedByModelViewSet):
    queryset = Notification.objects.select_related("user").all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "channel", "is_read"]


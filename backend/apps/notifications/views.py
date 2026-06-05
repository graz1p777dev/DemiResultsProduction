from rest_framework.permissions import IsAuthenticated

from common.views import CreatedByModelViewSet

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(CreatedByModelViewSet):
    queryset = Notification.objects.select_related("user").all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "channel", "is_read"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser or self.request.user.role in {"OWNER", "ADMIN", "MANAGER"}:
            return queryset
        return queryset.filter(user=self.request.user)

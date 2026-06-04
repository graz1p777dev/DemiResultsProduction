from rest_framework import viewsets

from common.permissions import IsOwnerAdminManager

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("actor").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsOwnerAdminManager]
    filterset_fields = ["actor", "action", "entity_type", "entity_id"]
    search_fields = ["action", "entity_type", "entity_id", "user_agent"]


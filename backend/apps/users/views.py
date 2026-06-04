from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets

from common.permissions import IsOwnerAdminManager

from .models import ClientProfile, StaffProfile
from .serializers import ClientProfileSerializer, StaffProfileSerializer, UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [IsOwnerAdminManager]
    search_fields = ["username", "email", "phone", "first_name", "last_name"]
    ordering_fields = ["id", "date_joined", "role"]


class ClientProfileViewSet(viewsets.ModelViewSet):
    queryset = ClientProfile.objects.select_related("user").all()
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.select_related("user").all()
    serializer_class = StaffProfileSerializer
    permission_classes = [IsOwnerAdminManager]


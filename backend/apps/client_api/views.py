from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bonuses.services import get_or_create_account
from apps.consultations.models import Consultation, ConsultationMessage
from apps.orders import services as order_services
from apps.orders.models import Order
from apps.products.models import Brand, Category, Product
from .serializers import (
    CatalogBrandSerializer,
    CatalogCategorySerializer,
    CatalogProductSerializer,
    ClientBonusAccountSerializer,
    ClientConsultationMessageSerializer,
    ClientConsultationSerializer,
    ClientOrderCreateSerializer,
    ClientOrderSerializer,
    MeSerializer,
)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Me"], responses={200: MeSerializer}, description="Return current client user and skin-card profile.")
    def get(self, request):
        return Response(MeSerializer(request.user).data)

    @extend_schema(tags=["Me"], request=MeSerializer, responses={200: MeSerializer}, description="Update current client user and profile fields.")
    def patch(self, request):
        serializer = MeSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(MeSerializer(user).data)


@extend_schema_view(list=extend_schema(tags=["Catalog"]), retrieve=extend_schema(tags=["Catalog"]))
class CatalogCategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.filter(is_active=True).order_by("name")
    serializer_class = CatalogCategorySerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    search_fields = ["name", "slug"]


@extend_schema_view(list=extend_schema(tags=["Catalog"]), retrieve=extend_schema(tags=["Catalog"]))
class CatalogBrandViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Brand.objects.filter(is_active=True).order_by("name")
    serializer_class = CatalogBrandSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    search_fields = ["name", "slug"]


@extend_schema_view(
    list=extend_schema(tags=["Catalog"], description="Public active product catalog without cost prices or staff-only fields."),
    retrieve=extend_schema(tags=["Catalog"], description="Public active product detail without cost prices or staff-only fields."),
)
class CatalogProductViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = (
        Product.objects.filter(is_active=True, category__is_active=True, brand__is_active=True)
        .select_related("category", "brand")
        .prefetch_related("images", "variants")
        .order_by("name")
    )
    serializer_class = CatalogProductSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    filterset_fields = ["category", "brand"]
    search_fields = ["name", "sku", "barcode", "description", "ingredients"]
    ordering_fields = ["name", "price", "stock_quantity"]


@extend_schema_view(
    list=extend_schema(tags=["Me"], description="List current client's orders."),
    retrieve=extend_schema(tags=["Me"], description="Get current client's order."),
    create=extend_schema(tags=["Me"], request=ClientOrderCreateSerializer, responses={201: ClientOrderSerializer}, description="Create an order for current client. Prices are fixed by backend."),
)
class MyOrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.none()
    serializer_class = ClientOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status"]
    ordering_fields = ["created_at", "total"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        return Order.objects.filter(client=self.request.user).select_related("warehouse").prefetch_related("items__product", "items__variant").order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return ClientOrderCreateSerializer
        return ClientOrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            order = serializer.save()
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(ClientOrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["Me"], description="Cancel current client's order before packing.")
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        try:
            order = order_services.cancel_order(order=self.get_object(), created_by=request.user, comment=request.data.get("comment", ""))
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(ClientOrderSerializer(order).data)


class MyBonusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=["Me"], responses={200: ClientBonusAccountSerializer}, description="Return current client's bonus balance and transactions.")
    def get(self, request):
        account = get_or_create_account(request.user)
        account = account.__class__.objects.prefetch_related("transactions").get(pk=account.pk)
        return Response(ClientBonusAccountSerializer(account).data)


@extend_schema_view(
    list=extend_schema(tags=["Me"], description="List current client's consultations."),
    retrieve=extend_schema(tags=["Me"], description="Get current client's consultation."),
    create=extend_schema(tags=["Me"], request=ClientConsultationSerializer, responses={201: ClientConsultationSerializer}, description="Request a consultation for current client."),
)
class MyConsultationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Consultation.objects.none()
    serializer_class = ClientConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status"]
    ordering_fields = ["scheduled_at", "created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Consultation.objects.none()
        return Consultation.objects.filter(client=self.request.user).order_by("-scheduled_at")

    def perform_create(self, serializer):
        serializer.save(client=self.request.user, created_by=self.request.user)

    @extend_schema(tags=["Me"], responses={200: ClientConsultationMessageSerializer(many=True)}, description="List messages for current client's consultation.")
    @action(detail=True, methods=["get", "post"])
    def messages(self, request, pk=None):
        consultation = self.get_object()
        if request.method == "GET":
            messages = ConsultationMessage.objects.filter(consultation=consultation).select_related("sender").order_by("created_at")
            return Response(ClientConsultationMessageSerializer(messages, many=True).data)
        serializer = ClientConsultationMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(consultation=consultation, sender=request.user, created_by=request.user)
        return Response(ClientConsultationMessageSerializer(message).data, status=status.HTTP_201_CREATED)

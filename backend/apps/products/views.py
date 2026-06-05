from drf_spectacular.utils import extend_schema, extend_schema_view

from common.permissions import IsStaffOperator
from common.views import CreatedByModelViewSet

from .models import Brand, Category, Product, ProductBatch, ProductImage, ProductVariant
from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ProductBatchSerializer,
    ProductImageSerializer,
    ProductSerializer,
    ProductVariantSerializer,
)


@extend_schema_view(list=extend_schema(tags=["Products"]), create=extend_schema(tags=["Products"]))
class CategoryViewSet(CreatedByModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOperator]
    search_fields = ["name", "slug"]


@extend_schema_view(list=extend_schema(tags=["Products"]), create=extend_schema(tags=["Products"]))
class BrandViewSet(CreatedByModelViewSet):
    queryset = Brand.objects.all().order_by("name")
    serializer_class = BrandSerializer
    permission_classes = [IsStaffOperator]
    search_fields = ["name", "slug"]


@extend_schema_view(list=extend_schema(tags=["Products"], description="List products with denormalized total stock."), create=extend_schema(tags=["Products"]))
class ProductViewSet(CreatedByModelViewSet):
    queryset = Product.objects.select_related("category", "brand").all().order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["category", "brand", "is_active"]
    search_fields = ["name", "sku", "barcode", "description"]
    ordering_fields = ["name", "price", "stock_quantity", "created_at"]


@extend_schema_view(list=extend_schema(tags=["Products"]), create=extend_schema(tags=["Products"]))
class ProductImageViewSet(CreatedByModelViewSet):
    queryset = ProductImage.objects.select_related("product").all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["product", "is_primary"]


@extend_schema_view(list=extend_schema(tags=["Products"]), create=extend_schema(tags=["Products"]))
class ProductVariantViewSet(CreatedByModelViewSet):
    queryset = ProductVariant.objects.select_related("product").all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["product", "is_active"]
    search_fields = ["name", "sku", "barcode", "product__name"]
    ordering_fields = ["name", "retail_price", "created_at"]


@extend_schema_view(list=extend_schema(tags=["Products"]), create=extend_schema(tags=["Products"]))
class ProductBatchViewSet(CreatedByModelViewSet):
    queryset = ProductBatch.objects.select_related("product", "variant").all()
    serializer_class = ProductBatchSerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["product", "variant", "batch_number"]
    search_fields = ["batch_number", "product__name", "product__sku", "variant__sku"]
    ordering_fields = ["expires_at", "received_at", "created_at"]

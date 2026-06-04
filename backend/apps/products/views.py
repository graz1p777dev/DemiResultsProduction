from common.permissions import IsStaffOperator
from common.views import CreatedByModelViewSet

from .models import Brand, Category, Product, ProductImage
from .serializers import BrandSerializer, CategorySerializer, ProductImageSerializer, ProductSerializer


class CategoryViewSet(CreatedByModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOperator]
    search_fields = ["name", "slug"]


class BrandViewSet(CreatedByModelViewSet):
    queryset = Brand.objects.all().order_by("name")
    serializer_class = BrandSerializer
    permission_classes = [IsStaffOperator]
    search_fields = ["name", "slug"]


class ProductViewSet(CreatedByModelViewSet):
    queryset = Product.objects.select_related("category", "brand").all().order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["category", "brand", "is_active"]
    search_fields = ["name", "sku", "barcode", "description"]
    ordering_fields = ["name", "price", "stock_quantity", "created_at"]


class ProductImageViewSet(CreatedByModelViewSet):
    queryset = ProductImage.objects.select_related("product").all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsStaffOperator]
    filterset_fields = ["product", "is_primary"]


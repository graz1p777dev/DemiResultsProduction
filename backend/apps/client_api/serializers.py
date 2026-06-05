from django.db import transaction
from rest_framework import serializers

from apps.bonuses.models import BonusAccount, BonusTransaction
from apps.bonuses.services import get_or_create_account
from apps.consultations.models import Consultation, ConsultationMessage
from apps.orders import services as order_services
from apps.orders.models import Order, OrderItem
from apps.products.models import Brand, Category, Product, ProductImage, ProductVariant
from apps.users.models import ClientProfile
from common.validators import kyrgyz_phone_validator


class CatalogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class CatalogBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug"]


class CatalogProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_primary"]


class CatalogProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ["id", "product", "name", "sku", "barcode", "size", "color", "retail_price", "is_active"]


class CatalogProductSerializer(serializers.ModelSerializer):
    category = CatalogCategorySerializer(read_only=True)
    brand = CatalogBrandSerializer(read_only=True)
    images = CatalogProductImageSerializer(many=True, read_only=True)
    variants = CatalogProductVariantSerializer(many=True, read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "brand",
            "name",
            "sku",
            "barcode",
            "description",
            "ingredients",
            "usage_instructions",
            "price",
            "stock_quantity",
            "is_low_stock",
            "images",
            "variants",
        ]


class ClientProfilePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = [
            "birth_date",
            "gender",
            "skin_type",
            "skin_concerns",
            "allergies",
            "complaints",
            "contraindications",
            "current_routine",
            "previous_treatments",
            "ai_summary",
            "recommendations",
            "staff_notes",
            "notes",
            "total_orders",
            "total_spent",
        ]
        read_only_fields = ["ai_summary", "recommendations", "staff_notes", "total_orders", "total_spent"]


class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True, validators=[kyrgyz_phone_validator])
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    role = serializers.CharField(read_only=True)
    client_profile = ClientProfilePublicSerializer(required=False)

    def to_representation(self, user):
        profile, _ = ClientProfile.objects.get_or_create(user=user)
        return {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "client_profile": ClientProfilePublicSerializer(profile).data,
        }

    @transaction.atomic
    def update(self, user, validated_data):
        profile_data = validated_data.pop("client_profile", None)
        for field in ["phone", "first_name", "last_name"]:
            if field in validated_data:
                setattr(user, field, validated_data[field] or None if field == "phone" else validated_data[field])
        user.save(update_fields=["phone", "first_name", "last_name"])
        if profile_data is not None:
            profile, _ = ClientProfile.objects.get_or_create(user=user)
            for field, value in profile_data.items():
                setattr(profile, field, value)
            profile.save()
        return user


class ClientOrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    variant_name = serializers.CharField(source="variant.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "variant", "variant_name", "quantity", "unit_price", "line_total"]
        read_only_fields = ["unit_price"]


class ClientOrderSerializer(serializers.ModelSerializer):
    items = ClientOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "warehouse", "subtotal", "delivery_price", "discount_total", "total", "comment", "created_at", "updated_at", "items"]
        read_only_fields = ["id", "status", "subtotal", "discount_total", "total", "created_at", "updated_at"]


class ClientOrderCreateItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True))
    variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.filter(is_active=True), required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        variant = attrs.get("variant")
        if variant and variant.product_id != attrs["product"].id:
            raise serializers.ValidationError("Variant must belong to selected product.")
        return attrs


class ClientOrderCreateSerializer(serializers.Serializer):
    warehouse = serializers.IntegerField(required=False, allow_null=True)
    delivery_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, default=0)
    comment = serializers.CharField(required=False, allow_blank=True)
    items = ClientOrderCreateItemSerializer(many=True, min_length=1)

    def validate_warehouse(self, value):
        if value is None:
            return value
        from apps.inventory.models import Warehouse

        if not Warehouse.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Warehouse does not exist.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        from apps.inventory.models import Warehouse

        items = validated_data.pop("items")
        warehouse_id = validated_data.pop("warehouse", None)
        warehouse = Warehouse.objects.get(pk=warehouse_id) if warehouse_id else None
        order = order_services.create_order(client=self.context["request"].user, warehouse=warehouse, created_by=self.context["request"].user, **validated_data)
        for item in items:
            order_services.add_order_item(order=order, product=item["product"], variant=item.get("variant"), quantity=item["quantity"])
        order.refresh_from_db()
        return order


class ClientBonusTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusTransaction
        fields = ["id", "transaction_type", "amount", "reason", "created_at"]


class ClientBonusAccountSerializer(serializers.ModelSerializer):
    transactions = ClientBonusTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = BonusAccount
        fields = ["id", "balance", "transactions"]

    @staticmethod
    def for_user(user):
        return get_or_create_account(user)


class ClientConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ["id", "scheduled_at", "status", "questionnaire", "recommendations", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "recommendations", "created_at", "updated_at"]


class ClientConsultationMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.get_full_name", read_only=True)

    class Meta:
        model = ConsultationMessage
        fields = ["id", "consultation", "sender", "sender_name", "text", "created_at"]
        read_only_fields = ["id", "consultation", "sender", "sender_name", "created_at"]

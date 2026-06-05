from decimal import Decimal

from django.contrib.auth import get_user_model

from apps.inventory.models import Branch, Warehouse
from apps.inventory import services as inventory_service
from apps.products.models import Brand, Category, Product


def make_user(username="user", role="CLIENT", password="pass12345"):
    User = get_user_model()
    user = User.objects.create_user(username=username, email=f"{username}@example.com", password=password, role=role)
    return user


def make_product(created_by=None, sku="SKU-1", price=Decimal("100.00"), cost=Decimal("60.00")):
    category = Category.objects.create(name=f"Category {sku}", slug=f"category-{sku.lower()}", created_by=created_by)
    brand = Brand.objects.create(name=f"Brand {sku}", slug=f"brand-{sku.lower()}", created_by=created_by)
    return Product.objects.create(
        category=category,
        brand=brand,
        name=f"Product {sku}",
        sku=sku,
        barcode=f"BAR-{sku}",
        price=price,
        cost_price=cost,
        created_by=created_by,
    )


def make_warehouse(created_by=None, code="MAIN"):
    branch = Branch.objects.create(name=f"Branch {code}", code=f"BR-{code}", created_by=created_by)
    return Warehouse.objects.create(branch=branch, name=f"Warehouse {code}", code=f"WH-{code}", created_by=created_by)


def receive_stock(product, warehouse, quantity, created_by=None):
    return inventory_service.receive_stock(
        product=product,
        warehouse=warehouse,
        quantity=quantity,
        reason="Test receipt",
        created_by=created_by,
    )

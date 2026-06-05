from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.bonuses import services as bonus_services
from apps.consultations.models import Consultation
from apps.inventory.models import Branch, StockLevel, StockMovement, Warehouse
from apps.orders import services as order_services
from apps.products.models import Brand, Category, Product, ProductBatch, ProductVariant
from apps.users.models import ClientProfile


DEMO_PRODUCTS = [
    {
        "category": ("Очищение", "cleansing"),
        "brand": ("DemiLab", "demilab"),
        "name": "DemiLab Gentle Cleansing Gel",
        "sku": "DL-CLEAN-GEL-150",
        "barcode": "9960000000011",
        "price": Decimal("890.00"),
        "cost_price": Decimal("510.00"),
        "description": "Мягкий гель для ежедневного очищения кожи.",
        "ingredients": "Aqua, Glycerin, Panthenol, Mild Surfactants",
        "usage": "Нанести на влажную кожу, вспенить, смыть водой.",
        "low_stock_threshold": 8,
        "batch": ("DLG-2026-01", "2027-12-31", Decimal("510.00")),
        "quantity": 24,
        "variants": [
            ("150 мл", "DL-CLEAN-GEL-150-V", "9960000000110", "150 мл", Decimal("890.00"), Decimal("510.00"), 16),
        ],
    },
    {
        "category": ("Увлажнение", "hydration"),
        "brand": ("DemiLab", "demilab"),
        "name": "DemiLab Barrier Repair Cream",
        "sku": "DL-BARRIER-CREAM-50",
        "barcode": "9960000000028",
        "price": Decimal("1450.00"),
        "cost_price": Decimal("820.00"),
        "description": "Крем для восстановления защитного барьера кожи.",
        "ingredients": "Ceramide NP, Squalane, Glycerin, Panthenol",
        "usage": "Использовать утром и вечером после сыворотки.",
        "low_stock_threshold": 6,
        "batch": ("DLB-2026-02", "2027-10-31", Decimal("820.00")),
        "quantity": 18,
        "variants": [
            ("50 мл", "DL-BARRIER-CREAM-50-V", "9960000000127", "50 мл", Decimal("1450.00"), Decimal("820.00"), 12),
        ],
    },
    {
        "category": ("Сыворотки", "serums"),
        "brand": ("SkinTheory", "skintheory"),
        "name": "SkinTheory Niacinamide Serum 10%",
        "sku": "ST-NIACINAMIDE-30",
        "barcode": "9960000000035",
        "price": Decimal("1190.00"),
        "cost_price": Decimal("640.00"),
        "description": "Сыворотка с ниацинамидом для себорегуляции и ровного тона.",
        "ingredients": "Niacinamide, Zinc PCA, Hyaluronic Acid",
        "usage": "Нанести 2-3 капли перед кремом.",
        "low_stock_threshold": 5,
        "batch": ("STN-2026-01", "2027-09-30", Decimal("640.00")),
        "quantity": 15,
        "variants": [
            ("30 мл", "ST-NIACINAMIDE-30-V", "9960000000134", "30 мл", Decimal("1190.00"), Decimal("640.00"), 10),
        ],
    },
    {
        "category": ("SPF", "spf"),
        "brand": ("SunCare KG", "suncare-kg"),
        "name": "SunCare KG Daily SPF 50",
        "sku": "SC-DAILY-SPF50-50",
        "barcode": "9960000000042",
        "price": Decimal("1590.00"),
        "cost_price": Decimal("900.00"),
        "description": "Легкий дневной SPF 50 для города.",
        "ingredients": "UV Filters, Vitamin E, Aloe Vera",
        "usage": "Нанести за 15 минут до выхода на солнце.",
        "low_stock_threshold": 7,
        "batch": ("SCD-2026-03", "2027-08-31", Decimal("900.00")),
        "quantity": 20,
        "variants": [
            ("50 мл", "SC-DAILY-SPF50-50-V", "9960000000141", "50 мл", Decimal("1590.00"), Decimal("900.00"), 14),
        ],
    },
    {
        "category": ("Тоники", "toners"),
        "brand": ("AquaBalance", "aquabalance"),
        "name": "AquaBalance Hydrating Toner",
        "sku": "AB-HYDRATING-TONER-200",
        "barcode": "9960000000059",
        "price": Decimal("760.00"),
        "cost_price": Decimal("430.00"),
        "description": "Увлажняющий тонер для ежедневного ухода.",
        "ingredients": "Aqua, Betaine, Sodium Hyaluronate, Allantoin",
        "usage": "Нанести после очищения ладонями или ватным диском.",
        "low_stock_threshold": 10,
        "batch": ("ABT-2026-01", "2028-01-31", Decimal("430.00")),
        "quantity": 30,
        "variants": [
            ("200 мл", "AB-HYDRATING-TONER-200-V", "9960000000158", "200 мл", Decimal("760.00"), Decimal("430.00"), 18),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed a small demo cosmetics catalog with warehouse stock."

    def handle(self, *args, **options):
        with transaction.atomic():
            branch, _ = Branch.objects.update_or_create(
                code="MAIN",
                defaults={
                    "name": "DemiResults Main Branch",
                    "address": "Bishkek demo branch",
                    "is_active": True,
                },
            )
            warehouse, _ = Warehouse.objects.update_or_create(
                code="MAIN-STOCK",
                defaults={
                    "branch": branch,
                    "name": "Main Stock",
                    "is_active": True,
                },
            )

            product_count = 0
            variant_count = 0
            stock_count = 0

            for item in DEMO_PRODUCTS:
                category, _ = Category.objects.update_or_create(
                    slug=item["category"][1],
                    defaults={"name": item["category"][0], "is_active": True},
                )
                brand, _ = Brand.objects.update_or_create(
                    slug=item["brand"][1],
                    defaults={"name": item["brand"][0], "is_active": True},
                )
                product, _ = Product.objects.update_or_create(
                    sku=item["sku"],
                    defaults={
                        "category": category,
                        "brand": brand,
                        "name": item["name"],
                        "barcode": item["barcode"],
                        "description": item["description"],
                        "ingredients": item["ingredients"],
                        "usage_instructions": item["usage"],
                        "price": item["price"],
                        "cost_price": item["cost_price"],
                        "low_stock_threshold": item["low_stock_threshold"],
                        "is_active": True,
                    },
                )
                product_count += 1

                batch_number, expires_at, batch_cost = item["batch"]
                batch, _ = ProductBatch.objects.update_or_create(
                    product=product,
                    variant=None,
                    batch_number=batch_number,
                    defaults={
                        "expires_at": expires_at,
                        "received_at": timezone.localdate(),
                        "cost_price": batch_cost,
                    },
                )
                self._set_stock(product, warehouse, item["quantity"], batch=batch)
                stock_count += 1

                for name, sku, barcode, size, retail_price, cost_price, quantity in item["variants"]:
                    variant, _ = ProductVariant.objects.update_or_create(
                        sku=sku,
                        defaults={
                            "product": product,
                            "name": name,
                            "barcode": barcode,
                            "size": size,
                            "retail_price": retail_price,
                            "cost_price": cost_price,
                            "is_active": True,
                        },
                    )
                    variant_count += 1
                    variant_batch, _ = ProductBatch.objects.update_or_create(
                        product=product,
                        variant=variant,
                        batch_number=f"{batch_number}-{size.replace(' ', '')}",
                        defaults={
                            "expires_at": expires_at,
                            "received_at": timezone.localdate(),
                            "cost_price": cost_price,
                        },
                    )
                    self._set_stock(product, warehouse, quantity, variant=variant, batch=variant_batch)
                    stock_count += 1

            client = self._seed_client()
            self._seed_client_bonus(client)
            self._seed_client_order(client, warehouse)
            self._seed_client_consultation(client)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Seeded {product_count} products, {variant_count} variants, {stock_count} stock levels and demo client data."
                )
            )

    def _set_stock(self, product, warehouse, quantity, variant=None, batch=None):
        level, _ = StockLevel.objects.get_or_create(
            warehouse=warehouse,
            product=product,
            variant=variant,
            batch=batch,
            defaults={"quantity": 0},
        )
        if level.quantity == quantity:
            return
        StockMovement.objects.create(
            product=product,
            variant=variant,
            batch=batch,
            destination_warehouse=warehouse,
            movement_type=StockMovement.MovementType.INVENTORY,
            quantity=quantity,
            reason="Demo seed stock",
            reference="seed_demo_products",
        )

    def _seed_client(self):
        User = get_user_model()
        client, created = User.objects.update_or_create(
            email="client.demo@demiresults.local",
            defaults={
                "username": "client-demo",
                "phone": "+996700111222",
                "first_name": "Айнара",
                "last_name": "Demo",
                "role": User.Role.CLIENT,
                "is_active": True,
            },
        )
        if created or not client.has_usable_password():
            client.set_password("StrongPass12345!")
            client.save(update_fields=["password"])
        ClientProfile.objects.update_or_create(
            user=client,
            defaults={
                "skin_type": "combination",
                "skin_concerns": "сухость, покраснения, периодические высыпания",
                "allergies": "нет известных аллергий",
                "current_routine": "очищение, крем, SPF",
                "recommendations": "мягкое очищение, восстановление барьера, ежедневный SPF",
                "total_orders": 1,
                "total_spent": Decimal("1780.00"),
            },
        )
        return client

    def _seed_client_bonus(self, client):
        account = bonus_services.get_or_create_account(client)
        if account.balance < Decimal("250.00"):
            bonus_services.accrue_bonus(client=client, amount=Decimal("250.00"), reason="Demo welcome bonus")

    def _seed_client_order(self, client, warehouse):
        if client.orders.exists():
            return
        products = list(Product.objects.order_by("id")[:2])
        order = order_services.create_order(client=client, warehouse=warehouse, created_by=client, comment="Demo frontend order")
        for product in products:
            order_services.add_order_item(order=order, product=product, quantity=1)

    def _seed_client_consultation(self, client):
        Consultation.objects.get_or_create(
            client=client,
            scheduled_at=timezone.now() + timezone.timedelta(days=2),
            defaults={
                "questionnaire": {"concern": "сухость и подбор базового ухода"},
                "recommendations": "Начать с мягкого очищения и крема для восстановления барьера.",
                "created_by": client,
            },
        )

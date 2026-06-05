from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.inventory import services as inventory_service
from apps.inventory.models import StockMovement

from .models import Sale, SaleItem, SaleReturn


def calculate_sale_totals(sale):
    items = list(sale.items.all())
    subtotal = sum((item.line_total for item in items), Decimal("0"))
    cost_total = sum((item.cost_total for item in items), Decimal("0"))
    total = max(subtotal - sale.discount_total - sale.bonus_spent, Decimal("0"))
    profit = calculate_profit(total=total, cost_total=cost_total)
    return subtotal, cost_total, total, profit


def calculate_profit(*, total, cost_total):
    return total - cost_total


def update_sale_totals(sale):
    sale.subtotal, sale.cost_total, sale.total, sale.profit = calculate_sale_totals(sale)
    sale.save(update_fields=["subtotal", "cost_total", "total", "profit", "updated_at"])
    return sale


@transaction.atomic
def create_sale(*, cashier, warehouse, client=None, created_by=None, status=Sale.Status.COMPLETED, discount_total=0, bonus_spent=0):
    sale = Sale(
        cashier=cashier,
        warehouse=warehouse,
        client=client,
        status=status,
        discount_total=discount_total,
        bonus_spent=bonus_spent,
        created_by=created_by or cashier,
    )
    sale.full_clean()
    sale.save()
    return sale


@transaction.atomic
def add_sale_item(*, sale, product, quantity, variant=None, batch=None):
    if sale.status in {Sale.Status.CANCELLED, Sale.Status.REFUNDED}:
        raise ValidationError("Cannot add items to cancelled or refunded sale.")
    if not sale.warehouse_id:
        raise ValidationError("Sale warehouse is required before adding items.")

    unit_price = variant.retail_price if variant else product.price
    unit_cost = batch.cost_price if batch else (variant.cost_price if variant else product.cost_price)
    item = SaleItem(
        sale=sale,
        product=product,
        variant=variant,
        batch=batch,
        quantity=quantity,
        unit_price=unit_price,
        unit_cost=unit_cost,
    )
    item.full_clean()
    item._skip_sale_item_service = True
    item.save()

    inventory_service.create_stock_movement(
        product=product,
        variant=variant,
        batch=batch,
        source_warehouse=sale.warehouse,
        movement_type=StockMovement.MovementType.SALE,
        quantity=quantity,
        reason="POS sale",
        reference=f"sale:{sale.pk}",
        created_by=sale.cashier,
    )
    update_sale_totals(sale)
    return item


@transaction.atomic
def complete_sale(sale):
    if sale.status == Sale.Status.CANCELLED:
        raise ValidationError("Cancelled sale cannot be completed.")
    sale.status = Sale.Status.COMPLETED
    sale.completed_at = sale.completed_at or timezone.now()
    sale.full_clean()
    sale.save(update_fields=["status", "completed_at", "updated_at"])
    update_sale_totals(sale)
    return sale


@transaction.atomic
def refund_sale(*, sale, created_by=None, reason=""):
    if sale.status in {Sale.Status.REFUNDED, Sale.Status.CANCELLED}:
        raise ValidationError("Sale cannot be returned in its current status.")
    if SaleReturn.objects.filter(sale=sale).exists():
        raise ValidationError("Sale has already been returned.")

    refund = SaleReturn(sale=sale, reason=reason, created_by=created_by, total_refund=Decimal("0"))
    refund._skip_sale_return_service = True
    refund.save()

    total_refund = Decimal("0")
    for item in sale.items.select_related("product", "variant", "batch"):
        inventory_service.create_stock_movement(
            product=item.product,
            variant=item.variant,
            batch=item.batch,
            destination_warehouse=sale.warehouse,
            movement_type=StockMovement.MovementType.RETURN,
            quantity=item.quantity,
            reason="Sale return",
            reference=f"sale_return:{refund.pk}",
            created_by=created_by,
        )
        total_refund += item.line_total

    refund.total_refund = total_refund
    refund.save(update_fields=["total_refund", "updated_at"])
    sale.status = Sale.Status.REFUNDED
    sale.save(update_fields=["status", "updated_at"])
    return refund

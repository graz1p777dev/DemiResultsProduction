from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F

from apps.products.models import Product

from .models import StockLevel, StockMovement


def sync_product_total_stock(product_id):
    total = (
        StockLevel.objects.filter(product_id=product_id)
        .aggregate(total=models.Sum("quantity"))
        .get("total")
        or 0
    )
    Product.objects.filter(pk=product_id).update(stock_quantity=total)
    return total


def get_locked_stock_level(product, warehouse, variant=None, batch=None):
    level, _ = StockLevel.objects.select_for_update().get_or_create(
        warehouse=warehouse,
        product=product,
        variant=variant,
        batch=batch,
        defaults={"quantity": 0},
    )
    return level


def change_stock_level(product, warehouse, delta, variant=None, batch=None):
    level = get_locked_stock_level(product, warehouse, variant=variant, batch=batch)
    if delta < 0 and level.available_quantity < abs(delta):
        raise ValidationError("Insufficient stock in source warehouse.")
    level.quantity = F("quantity") + delta
    level.save(update_fields=["quantity", "updated_at"])
    level.refresh_from_db(fields=["quantity", "reserved_quantity"])
    level.full_clean()
    return level


@transaction.atomic
def apply_stock_movement(movement):
    if movement.pk:
        raise ValidationError("Stock movements are immutable after creation.")
    movement.full_clean()

    if movement.movement_type in {StockMovement.MovementType.OUT, StockMovement.MovementType.SALE, StockMovement.MovementType.TRANSFER}:
        change_stock_level(
            product=movement.product,
            warehouse=movement.source_warehouse,
            variant=movement.variant,
            batch=movement.batch,
            delta=-movement.quantity,
        )
    if movement.movement_type in {StockMovement.MovementType.IN, StockMovement.MovementType.RETURN, StockMovement.MovementType.TRANSFER}:
        change_stock_level(
            product=movement.product,
            warehouse=movement.destination_warehouse,
            variant=movement.variant,
            batch=movement.batch,
            delta=movement.quantity,
        )
    if movement.movement_type == StockMovement.MovementType.INVENTORY:
        level = get_locked_stock_level(
            product=movement.product,
            warehouse=movement.destination_warehouse,
            variant=movement.variant,
            batch=movement.batch,
        )
        level.quantity = movement.quantity
        level.full_clean()
        level.save(update_fields=["quantity", "updated_at"])

    movement._skip_stock_apply = True
    movement.save()
    sync_product_total_stock(movement.product_id)
    return movement


def create_stock_movement(*, product, movement_type, quantity, created_by=None, variant=None, batch=None, source_warehouse=None, destination_warehouse=None, reason="", reference=""):
    movement = StockMovement(
        product=product,
        variant=variant,
        batch=batch,
        source_warehouse=source_warehouse,
        destination_warehouse=destination_warehouse,
        movement_type=movement_type,
        quantity=quantity,
        reason=reason,
        reference=reference,
        created_by=created_by,
    )
    return apply_stock_movement(movement)


def receive_stock(*, product, warehouse, quantity, created_by=None, variant=None, batch=None, reason="Stock receipt", reference=""):
    return create_stock_movement(
        product=product,
        variant=variant,
        batch=batch,
        destination_warehouse=warehouse,
        movement_type=StockMovement.MovementType.IN,
        quantity=quantity,
        reason=reason,
        reference=reference,
        created_by=created_by,
    )


def write_off_stock(*, product, warehouse, quantity, created_by=None, variant=None, batch=None, reason="Stock write-off", reference=""):
    return create_stock_movement(
        product=product,
        variant=variant,
        batch=batch,
        source_warehouse=warehouse,
        movement_type=StockMovement.MovementType.OUT,
        quantity=quantity,
        reason=reason,
        reference=reference,
        created_by=created_by,
    )


def move_stock(*, product, source_warehouse, destination_warehouse, quantity, created_by=None, variant=None, batch=None, reason="Stock transfer", reference=""):
    return create_stock_movement(
        product=product,
        variant=variant,
        batch=batch,
        source_warehouse=source_warehouse,
        destination_warehouse=destination_warehouse,
        movement_type=StockMovement.MovementType.TRANSFER,
        quantity=quantity,
        reason=reason,
        reference=reference,
        created_by=created_by,
    )


def adjust_stock(*, product, warehouse, quantity, created_by=None, variant=None, batch=None, reason="Inventory adjustment", reference=""):
    return create_stock_movement(
        product=product,
        variant=variant,
        batch=batch,
        destination_warehouse=warehouse,
        movement_type=StockMovement.MovementType.INVENTORY,
        quantity=quantity,
        reason=reason,
        reference=reference,
        created_by=created_by,
    )


@transaction.atomic
def reserve_stock(*, product, warehouse, quantity, variant=None, batch=None):
    level = get_locked_stock_level(product, warehouse, variant=variant, batch=batch)
    if level.available_quantity < quantity:
        raise ValidationError("Insufficient available stock to reserve.")
    level.reserved_quantity = F("reserved_quantity") + quantity
    level.save(update_fields=["reserved_quantity", "updated_at"])
    level.refresh_from_db(fields=["quantity", "reserved_quantity"])
    level.full_clean()
    return level


@transaction.atomic
def release_reserved_stock(*, product, warehouse, quantity, variant=None, batch=None):
    level = get_locked_stock_level(product, warehouse, variant=variant, batch=batch)
    if level.reserved_quantity < quantity:
        raise ValidationError("Cannot release more reserved stock than exists.")
    level.reserved_quantity = F("reserved_quantity") - quantity
    level.save(update_fields=["reserved_quantity", "updated_at"])
    level.refresh_from_db(fields=["quantity", "reserved_quantity"])
    return level


@transaction.atomic
def consume_reserved_stock(*, product, warehouse, quantity, variant=None, batch=None, created_by=None, reason="Consume reserved stock", reference=""):
    level = get_locked_stock_level(product, warehouse, variant=variant, batch=batch)
    if level.reserved_quantity < quantity:
        raise ValidationError("Cannot consume more reserved stock than exists.")
    level.reserved_quantity = F("reserved_quantity") - quantity
    level.quantity = F("quantity") - quantity
    level.save(update_fields=["quantity", "reserved_quantity", "updated_at"])
    level.refresh_from_db(fields=["quantity", "reserved_quantity"])
    level.full_clean()
    movement = StockMovement(
        product=product,
        variant=variant,
        batch=batch,
        source_warehouse=warehouse,
        movement_type=StockMovement.MovementType.SALE,
        quantity=quantity,
        reason=reason,
        reference=reference,
        created_by=created_by,
    )
    movement._skip_stock_apply = True
    movement.full_clean()
    movement.save()
    sync_product_total_stock(product.id)
    return movement

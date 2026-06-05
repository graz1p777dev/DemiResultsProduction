from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.inventory import services as inventory_service
from apps.audit.services import log_event

from .models import Order, OrderItem, OrderStatusHistory


def calculate_order_totals(order):
    subtotal = sum((item.line_total for item in order.items.all()), Decimal("0"))
    total = max(subtotal + order.delivery_price - order.discount_total, Decimal("0"))
    return subtotal, total


def update_order_totals(order):
    order.subtotal, order.total = calculate_order_totals(order)
    order.save(update_fields=["subtotal", "total", "updated_at"])
    return order


@transaction.atomic
def create_order(*, client, warehouse=None, created_by=None, status=Order.Status.CREATED, delivery_price=0, discount_total=0, comment=""):
    order = Order(
        client=client,
        warehouse=warehouse,
        status=status,
        delivery_price=delivery_price,
        discount_total=discount_total,
        comment=comment,
        created_by=created_by or client,
    )
    order.full_clean()
    order.save()
    create_order_status_history(order=order, from_status="", to_status=order.status, created_by=created_by or client)
    return order


@transaction.atomic
def add_order_item(*, order, product, quantity, variant=None, batch=None):
    if order.status not in {Order.Status.CREATED, Order.Status.CONFIRMED}:
        raise ValidationError("Order items can be changed only before packing.")
    unit_price = variant.retail_price if variant else product.price
    item = OrderItem(order=order, product=product, variant=variant, batch=batch, quantity=quantity, unit_price=unit_price)
    item.full_clean()
    item._skip_order_item_service = True
    item.save()
    update_order_totals(order)
    return item


@transaction.atomic
def create_order_status_history(*, order, from_status, to_status, created_by=None, comment=""):
    return OrderStatusHistory.objects.create(
        order=order,
        from_status=from_status,
        to_status=to_status,
        comment=comment,
        created_by=created_by,
    )


@transaction.atomic
def change_order_status(*, order, to_status, created_by=None, comment=""):
    order = Order.objects.select_for_update().get(pk=order.pk)
    from_status = order.status
    if from_status == to_status:
        return order
    if to_status not in Order.ALLOWED_TRANSITIONS.get(from_status, set()):
        raise ValidationError(f"Cannot change order status from {from_status} to {to_status}.")
    if to_status == Order.Status.CONFIRMED and not order.stock_reserved:
        reserve_order_stock(order)
        order.stock_reserved = True
    if to_status == Order.Status.PACKING and order.stock_reserved:
        consume_order_reserved_stock(order, created_by=created_by)
        order.stock_reserved = False
    order.status = to_status
    order.save(update_fields=["status", "stock_reserved", "updated_at"])
    create_order_status_history(order=order, from_status=from_status, to_status=to_status, created_by=created_by, comment=comment)
    log_event(actor=created_by, action="order.status_changed", entity_type="order", entity_id=order.id, metadata={"from": from_status, "to": to_status})
    return order


def cancel_order(*, order, created_by=None, comment=""):
    if order.status == Order.Status.CANCELLED:
        raise ValidationError("Order is already cancelled.")
    if order.status not in Order.CANCELLABLE_STATUSES:
        raise ValidationError("Order can be cancelled only before packing.")
    order = Order.objects.select_for_update().get(pk=order.pk)
    if order.stock_reserved:
        release_order_reserved_stock(order)
        order.stock_reserved = False
        order.save(update_fields=["stock_reserved", "updated_at"])
    return change_order_status(order=order, to_status=Order.Status.CANCELLED, created_by=created_by, comment=comment)


def reserve_order_stock(order):
    if not order.warehouse_id:
        raise ValidationError("Order warehouse is required to reserve stock.")
    for item in order.items.select_related("product", "variant", "batch"):
        inventory_service.reserve_stock(
            product=item.product,
            variant=item.variant,
            batch=item.batch,
            warehouse=order.warehouse,
            quantity=item.quantity,
        )


def release_order_reserved_stock(order):
    if not order.warehouse_id:
        return
    for item in order.items.select_related("product", "variant", "batch"):
        inventory_service.release_reserved_stock(
            product=item.product,
            variant=item.variant,
            batch=item.batch,
            warehouse=order.warehouse,
            quantity=item.quantity,
        )


def consume_order_reserved_stock(order, created_by=None):
    if not order.warehouse_id:
        raise ValidationError("Order warehouse is required to consume reserved stock.")
    for item in order.items.select_related("product", "variant", "batch"):
        inventory_service.consume_reserved_stock(
            product=item.product,
            variant=item.variant,
            batch=item.batch,
            warehouse=order.warehouse,
            quantity=item.quantity,
            created_by=created_by,
            reason="Order packing",
            reference=f"order:{order.pk}",
        )

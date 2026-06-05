import pytest
from django.core.exceptions import ValidationError

from apps.inventory.models import StockLevel, StockMovement
from apps.inventory import services as inventory_service
from apps.orders.models import Order
from apps.orders import services as order_service
from apps.sales.models import Sale, SaleItem, SaleReturn
from apps.sales import services as sale_service

from .factories import make_product, make_user, make_warehouse, receive_stock


@pytest.mark.django_db
def test_stock_movement_receipt_and_sale_update_stock():
    manager = make_user("manager", role="MANAGER")
    product = make_product(created_by=manager)
    warehouse = make_warehouse(created_by=manager)

    receive_stock(product, warehouse, 5, created_by=manager)
    product.refresh_from_db()

    assert product.stock_quantity == 5
    assert StockLevel.objects.get(product=product, warehouse=warehouse).quantity == 5

    inventory_service.create_stock_movement(
        product=product,
        source_warehouse=warehouse,
        movement_type=StockMovement.MovementType.SALE,
        quantity=2,
        created_by=manager,
    )
    product.refresh_from_db()

    assert product.stock_quantity == 3
    assert StockLevel.objects.get(product=product, warehouse=warehouse).quantity == 3


@pytest.mark.django_db
def test_write_off_and_transfer_stock():
    manager = make_user("warehouse-manager", role="WAREHOUSE")
    product = make_product(created_by=manager, sku="SKU-TRANSFER")
    source = make_warehouse(created_by=manager, code="SRC")
    destination = make_warehouse(created_by=manager, code="DST")
    receive_stock(product, source, 10, created_by=manager)

    inventory_service.write_off_stock(product=product, warehouse=source, quantity=2, created_by=manager)
    inventory_service.move_stock(product=product, source_warehouse=source, destination_warehouse=destination, quantity=3, created_by=manager)

    assert StockLevel.objects.get(product=product, warehouse=source).quantity == 5
    assert StockLevel.objects.get(product=product, warehouse=destination).quantity == 3
    product.refresh_from_db()
    assert product.stock_quantity == 8


@pytest.mark.django_db
def test_cannot_sell_more_than_available_stock():
    cashier = make_user("cashier", role="CASHIER")
    product = make_product(created_by=cashier)
    warehouse = make_warehouse(created_by=cashier)
    receive_stock(product, warehouse, 1, created_by=cashier)

    sale = Sale.objects.create(cashier=cashier, warehouse=warehouse, created_by=cashier)

    with pytest.raises(ValidationError):
        sale_service.add_sale_item(sale=sale, product=product, quantity=2)


@pytest.mark.django_db
def test_sale_item_calculates_profit_and_return_restores_stock():
    cashier = make_user("cashier2", role="CASHIER")
    product = make_product(created_by=cashier)
    warehouse = make_warehouse(created_by=cashier)
    receive_stock(product, warehouse, 3, created_by=cashier)

    sale = Sale.objects.create(cashier=cashier, warehouse=warehouse, created_by=cashier)
    sale_service.add_sale_item(sale=sale, product=product, quantity=2)
    sale.refresh_from_db()
    product.refresh_from_db()

    assert sale.total == product.price * 2
    assert sale.profit == (product.price - product.cost_price) * 2
    assert product.stock_quantity == 1

    sale_service.refund_sale(sale=sale, created_by=cashier, reason="Test return")
    sale.refresh_from_db()
    product.refresh_from_db()

    assert sale.status == Sale.Status.REFUNDED
    assert product.stock_quantity == 3


@pytest.mark.django_db
def test_duplicate_sale_return_is_forbidden():
    cashier = make_user("cashier3", role="CASHIER")
    product = make_product(created_by=cashier, sku="SKU-RETURN")
    warehouse = make_warehouse(created_by=cashier, code="RET")
    receive_stock(product, warehouse, 2, created_by=cashier)
    sale = Sale.objects.create(cashier=cashier, warehouse=warehouse, created_by=cashier)
    sale_service.add_sale_item(sale=sale, product=product, quantity=1)
    sale_service.refund_sale(sale=sale, created_by=cashier)

    with pytest.raises(ValidationError):
        sale_service.refund_sale(sale=sale, created_by=cashier)


@pytest.mark.django_db
def test_order_cannot_be_cancelled_after_packing():
    client = make_user("client", role="CLIENT")
    manager = make_user("manager2", role="MANAGER")
    warehouse = make_warehouse(created_by=manager)
    order = Order.objects.create(client=client, warehouse=warehouse, status=Order.Status.PACKING, created_by=client)

    with pytest.raises(ValidationError):
        order.cancel()


@pytest.mark.django_db
def test_order_status_transition_writes_history_and_rejects_invalid_jump():
    client = make_user("client-status", role="CLIENT")
    manager = make_user("manager-status", role="MANAGER")
    warehouse = make_warehouse(created_by=manager, code="ORD")
    order = order_service.create_order(client=client, warehouse=warehouse, created_by=client)

    order_service.change_order_status(order=order, to_status=Order.Status.CONFIRMED, created_by=manager)
    order.refresh_from_db()

    assert order.status == Order.Status.CONFIRMED
    assert order.status_history.filter(from_status=Order.Status.CREATED, to_status=Order.Status.CONFIRMED).exists()

    with pytest.raises(ValidationError):
        order_service.change_order_status(order=order, to_status=Order.Status.COMPLETED, created_by=manager)


@pytest.mark.django_db
def test_order_confirm_reserves_and_packing_consumes_stock():
    client = make_user("client-reserve", role="CLIENT")
    manager = make_user("manager-reserve", role="MANAGER")
    product = make_product(created_by=manager, sku="SKU-RESERVE")
    warehouse = make_warehouse(created_by=manager, code="RSV")
    receive_stock(product, warehouse, 5, created_by=manager)
    order = order_service.create_order(client=client, warehouse=warehouse, created_by=client)
    order_service.add_order_item(order=order, product=product, quantity=2)

    order_service.change_order_status(order=order, to_status=Order.Status.CONFIRMED, created_by=manager)
    level = StockLevel.objects.get(product=product, warehouse=warehouse)
    assert level.quantity == 5
    assert level.reserved_quantity == 2

    order.refresh_from_db()
    order_service.change_order_status(order=order, to_status=Order.Status.PACKING, created_by=manager)
    level.refresh_from_db()
    product.refresh_from_db()
    assert level.quantity == 3
    assert level.reserved_quantity == 0
    assert product.stock_quantity == 3

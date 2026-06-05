# Architecture

DemiResults uses a backend-first architecture.

```text
Client Mobile App
Staff Mobile App
Admin Web Panel
        |
        v
Django REST API
        |
        v
PostgreSQL + Redis + Celery + n8n
```

The backend owns:

- prices
- stock
- discounts
- bonuses
- payment statuses
- order transitions
- role permissions

## Rule: Inventory Changes

Product stock must change only through `StockMovement`.

Direct stock changes outside stock movements are not part of the business flow and should be treated as bugs unless they are inside controlled maintenance scripts.

Stock is stored per warehouse in `StockLevel`. `Product.stock_quantity` is kept as a denormalized total for fast catalog reads and is synchronized by stock movements.

Supported stock movement types:

- `IN`: receipt into a destination warehouse
- `OUT`: write-off from a source warehouse
- `SALE`: POS sale from a source warehouse
- `RETURN`: return into a destination warehouse
- `TRANSFER`: move between source and destination warehouses
- `INVENTORY`: set the physical count for one warehouse/product key

Sales and returns also use stock movements, so inventory history stays complete.

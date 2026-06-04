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


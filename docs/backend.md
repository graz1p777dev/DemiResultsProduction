# Backend

The backend is the source of truth for prices, stock, statuses, bonuses and permissions.

## Service Layer

Business operations live in `services.py` files:

- `apps.inventory.services`: stock receipt, write-off, transfer, adjustment, reservation and product stock synchronization.
- `apps.sales.services`: sale creation, sale item write-off, totals, profit and refunds.
- `apps.orders.services`: order creation, item creation, status transitions, cancellation and status history.
- `apps.bonuses.services`: bonus accrual, spend, rollback and bonus calculation.
- `apps.ai_assistant.services`: AI client lookup, conversation/message persistence and safe product payloads.

Models keep structural validation and compatibility. ViewSets should stay thin and call services for domain operations.

## Inventory

Physical stock is stored in `StockLevel` per warehouse/product/variant/batch.

All stock changes go through `StockMovement` and inventory services. The services use `transaction.atomic()` and `select_for_update()` to avoid race conditions and reject negative stock.

`Product.stock_quantity` is a denormalized total synchronized after stock movements.

## Sales

A sale belongs to a warehouse and cashier. Sale items fix retail price and cost at the moment of sale. Adding a sale item writes off stock through inventory services. Refunds are one-time and restore stock through a return stock movement.

Profit is calculated as sale total minus fixed item costs.

## Orders

Orders have strict status transitions:

```text
CREATED -> CONFIRMED -> PACKING -> DELIVERING -> COMPLETED
CREATED -> CANCELLED
CONFIRMED -> CANCELLED
```

Cancellation is allowed only before `PACKING`. Every status change is recorded in `OrderStatusHistory`.

When an order moves to `CONFIRMED`, stock is reserved through inventory services. When it moves to `PACKING`, reserved stock is consumed and converted to stock movement history. Cancelling before packing releases reserved stock.

## Payments

Payment operations live in `apps.payments.services`.

Supported service flows:

- create payment linked to order or sale
- create local online payment with `LOCAL-...` provider reference
- mark payment as paid
- fail pending local payment
- refund a paid payment

Payment events also write domain audit logs. The local provider is for development only and never accepts card/bank payloads.

## CI

`.github/workflows/backend.yml` runs backend build, migration check, migrations, Django checks, tests and OpenAPI validation.

## Background Tasks

Celery task modules:

- `apps.reports.tasks.cleanup_old_report_exports`
- `apps.reports.tasks.create_database_backup`
- `apps.reports.tasks.cleanup_old_database_backups`
- `apps.notifications.tasks.mark_notification_sent`
- `apps.ai_assistant.tasks.cleanup_invalid_webhook_logs`

Database backups use `pg_dump` inside the backend image and write to `BACKUP_DIR`, which is ignored by git in local development. `docker-compose.yml` includes `celery-beat` with daily cleanup/backup schedules.

## Health

`GET /api/health/` checks PostgreSQL and Redis and returns `200` when both dependencies are reachable. It is public and does not expose secrets.

## AI Webhook

The n8n webhook is available at `/api/ai/webhook/`.

It requires:

- `Authorization: Token <N8N_API_TOKEN>`
- `X-Demi-Signature: <hmac-sha256 raw body>`

The webhook can find a client by Kyrgyz phone, Telegram username, external AI id or name, then saves the conversation/message and returns a safe product payload.

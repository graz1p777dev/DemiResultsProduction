# DemiResults

DemiResults is a backend-first system for a skincare cosmetics store.

The backend is the source of truth for prices, stock, roles, bonuses, payment state, and order state. Clients only send requests; business decisions are made by the API.

## Current Scope

This repository currently contains the initial Django backend structure and placeholders for mobile and web apps.

MVP backend modules:

- JWT authentication and roles
- Products, categories, brands, images, barcodes
- Inventory and stock movements
- POS sales and sale returns
- Orders and cart-like order items
- Payments
- Delivery
- Bonuses and promo codes
- Consultations
- AI assistant webhook endpoint
- Notifications
- Audit log
- Excel reports

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

API docs:

- Swagger: http://localhost:8000/api/docs/
- Redoc: http://localhost:8000/api/redoc/
- Admin: http://localhost:8000/admin/

Create a superuser:

```bash
docker compose exec backend python manage.py createsuperuser
```

## Local Development Without Docker

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/local.txt
python manage.py migrate
python manage.py runserver
```

## Project Layout

```text
demiresults/
├── backend/
│   ├── core/
│   │   ├── settings/
│   │   ├── urls.py
│   │   ├── celery.py
│   │   └── asgi.py
│   ├── apps/
│   ├── common/
│   ├── manage.py
│   ├── requirements/
│   └── Dockerfile
├── mobile/
├── web/
├── infra/
├── docs/
└── docker-compose.yml
```

## Security Baseline

- JWT access and refresh tokens
- Role-based permissions
- Dedicated n8n token and signed webhook support
- Rate limiting via DRF throttles
- CORS and CSRF origins controlled by environment variables
- Secrets kept outside code in `.env`
- Audit logs for important business actions


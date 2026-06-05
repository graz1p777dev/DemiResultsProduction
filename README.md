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

Frontend previews:

```bash
cd web
python3 -m http.server 3000
```

- Client mobile UI: http://localhost:3000/client_site/
- Admin desktop UI: http://localhost:3000/admin_panel/

Client-facing API:

- `GET/PATCH /api/me/`
- `GET /api/me/bonuses/`
- `GET/POST /api/me/orders/`
- `POST /api/me/orders/{id}/cancel/`
- `GET/POST /api/me/consultations/`
- `GET/POST /api/me/consultations/{id}/messages/`
- `GET /api/catalog/categories/`
- `GET /api/catalog/brands/`
- `GET /api/catalog/products/`

Create a superuser:

```bash
docker compose exec backend python manage.py createsuperuser
```

Seed a small demo product database:

```bash
docker compose exec backend python manage.py seed_demo_products
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
- Email/password registration through `/api/auth/register/`
- Phone/email + password login through `/api/auth/token/`
- Google OAuth login/register through `/api/auth/google/`
- Local phone-code login through `/api/auth/phone/request-code/` and `/api/auth/phone/verify/`
- Logout through `/api/auth/logout/`
- Password change through `/api/auth/password/change/`
- Password reset through `/api/auth/password/reset/` and `/api/auth/password/reset/confirm/`
- Role-based permissions
- Dedicated n8n token and signed webhook support
- Rate limiting via DRF throttles
- CORS and CSRF origins controlled by environment variables
- Secrets kept outside code in `.env`
- Audit logs for important business actions

## Backend Notes

Business logic is organized in service modules:

- `backend/apps/inventory/services.py`
- `backend/apps/sales/services.py`
- `backend/apps/orders/services.py`
- `backend/apps/bonuses/services.py`
- `backend/apps/ai_assistant/services.py`

See `docs/backend.md` for the service layer, stock, sales, orders and AI webhook flow.
See `docs/frontend-contract.md` for frontend API payloads and UI tokens.
See `docs/production-readiness.md` for the production preparation checklist.

Operational action endpoints now exist for critical flows:

- `POST /api/inventory/stock-movements/receive/`
- `POST /api/inventory/stock-movements/write-off/`
- `POST /api/inventory/stock-movements/transfer/`
- `POST /api/sales/sales/{id}/complete/`
- `POST /api/sales/sales/{id}/refund/`
- `POST /api/orders/orders/{id}/cancel/`
- `POST /api/orders/orders/{id}/change-status/`
- `POST /api/payments/payments/{id}/mark-paid/`
- `POST /api/payments/payments/local/`
- `POST /api/payments/payments/{id}/confirm-local/`
- `POST /api/payments/payments/{id}/fail-local/`
- `POST /api/payments/payments/{id}/refund/`

Celery tasks are available for report cleanup, local database backups, backup retention, AI webhook cleanup and notification processing. `docker-compose.yml` includes `celery` and `celery-beat`.

Health check:

- `GET /api/health/`

## Google OAuth

Set `GOOGLE_CLIENT_ID` in `.env`.

Frontend or mobile sends only the Google `id_token`:

```bash
POST /api/auth/google/
{
  "id_token": "GOOGLE_ID_TOKEN"
}
```

The backend verifies the token with Google, checks the audience and verified email, creates or links the user, creates `ClientProfile`, and returns DemiResults JWT tokens.

## Registration

```bash
POST /api/auth/register/
{
  "email": "client@example.com",
  "phone": "+996700111222",
  "password": "StrongPass12345!",
  "first_name": "Ainara"
}
```

The backend validates the password with Django password validators, creates a CLIENT user and `ClientProfile`, then returns JWT tokens.

## Local Phone Auth

Set `SMS_PROVIDER=console`. Request code:

```bash
POST /api/auth/phone/request-code/
{
  "phone": "+996700111222"
}
```

The 6-digit code is printed in the backend/Celery terminal logs. Verify it:

```bash
POST /api/auth/phone/verify/
{
  "phone": "+996700111222",
  "code": "123456"
}
```

The backend returns DemiResults JWT tokens and creates a CLIENT user/profile for a new phone.

## Local Payments

Set `PAYMENT_PROVIDER=local`. Local online payments do not accept or store card data. They create a `LOCAL-...` reference and can be confirmed or failed through staff-only API actions.

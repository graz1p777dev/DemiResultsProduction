# Frontend Contract

This document describes the API surface that client/mobile and admin frontend should use.

## Base URL

Local development:

```text
http://localhost:8000
```

Static frontend preview:

```text
http://localhost:3000/client_site/
http://localhost:3000/admin_panel/
```

## Auth

Register:

```http
POST /api/auth/register/
```

Request:

```json
{
  "email": "client@example.com",
  "phone": "+996700111222",
  "password": "StrongPass12345!",
  "first_name": "Ainara",
  "last_name": "T"
}
```

Response:

```json
{
  "access": "...",
  "refresh": "...",
  "user": {
    "id": 1,
    "email": "client@example.com",
    "phone": "+996700111222",
    "first_name": "Ainara",
    "last_name": "T",
    "role": "CLIENT",
    "has_client_profile": true
  }
}
```

Login with email or phone:

```http
POST /api/auth/token/
```

Request:

```json
{
  "username": "client@example.com",
  "password": "StrongPass12345!"
}
```

Google:

```http
POST /api/auth/google/
```

The frontend sends only `id_token`. It must never send `google_id` directly.

Phone code:

```http
POST /api/auth/phone/request-code/
POST /api/auth/phone/verify/
```

Local development uses `SMS_PROVIDER=console`, so the code appears in backend terminal logs.

## Client API

Current user:

```http
GET /api/me/
PATCH /api/me/
```

Patch request:

```json
{
  "first_name": "Ainara",
  "client_profile": {
    "skin_type": "dry",
    "skin_concerns": "dryness, redness"
  }
}
```

Catalog:

```http
GET /api/catalog/categories/
GET /api/catalog/brands/
GET /api/catalog/products/
GET /api/catalog/products/{id}/
```

Catalog product response intentionally excludes:

- `cost_price`
- `created_by`
- supplier/internal warehouse movement fields

Orders:

```http
GET /api/me/orders/
POST /api/me/orders/
POST /api/me/orders/{id}/cancel/
```

Create order:

```json
{
  "items": [
    {
      "product": 1,
      "variant": null,
      "quantity": 2
    }
  ],
  "comment": "Call before delivery"
}
```

Bonuses:

```http
GET /api/me/bonuses/
```

Consultations:

```http
GET /api/me/consultations/
POST /api/me/consultations/
GET /api/me/consultations/{id}/messages/
POST /api/me/consultations/{id}/messages/
```

Create consultation:

```json
{
  "scheduled_at": "2026-07-01T10:00:00+06:00",
  "questionnaire": {
    "concern": "dryness"
  }
}
```

## Admin API

Admin panel can use staff endpoints after staff JWT login:

- `/api/products/`
- `/api/inventory/`
- `/api/sales/`
- `/api/orders/`
- `/api/payments/`
- `/api/reports/`
- `/api/audit/`

The current static admin preview reads public catalog and health without auth, and falls back to demo data where staff auth is required.

## UI Style

Use DemiResults palette:

- Navy: `#081526`
- Mid: `#24456F`
- Accent: `#BFD8FB`
- Soft: `#E6F0FB`
- BG: `#F6F8FB`
- Muted: `#929BAD`

Typography:

- Display: 26px light/regular
- H1: 22px medium
- Body: 15px regular
- Caption: 12px

Client frontend is mobile-first. Admin frontend is desktop-first.

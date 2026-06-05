# API Notes

Swagger is available at `/api/docs/`.

JWT endpoints:

- `POST /api/auth/register/`
- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`
- `POST /api/auth/google/`
- `POST /api/auth/phone/request-code/`
- `POST /api/auth/phone/verify/`

`/api/auth/token/` accepts email, Kyrgyz phone number or username in the `username` field plus password.

Registration:

```http
POST /api/auth/register/
Content-Type: application/json

{
  "email": "client@example.com",
  "phone": "+996700111222",
  "password": "StrongPass12345!",
  "first_name": "Ainara",
  "last_name": "T"
}
```

The backend validates the password through Django password validators, creates a CLIENT user/profile and returns `access`/`refresh`.

Google OAuth:

```http
POST /api/auth/google/
Content-Type: application/json

{"id_token": "GOOGLE_ID_TOKEN"}
```

The client must not send `google_id` directly. Backend verifies the Google `id_token`, links or creates a client user, creates `ClientProfile`, and returns `access` and `refresh` JWT tokens.

Phone-code auth:

```http
POST /api/auth/phone/request-code/
Content-Type: application/json

{"phone": "+996700111222"}
```

With `SMS_PROVIDER=console`, the backend prints a 6-digit code in terminal logs. The client verifies it:

```http
POST /api/auth/phone/verify/
Content-Type: application/json

{"phone": "+996700111222", "code": "123456"}
```

The backend creates a CLIENT user and `ClientProfile` for new phones and returns JWT tokens. Codes are stored only as password hashes.

n8n endpoint:

- `POST /api/ai/webhook/`

n8n requests must include:

- `Authorization: Token <N8N_API_TOKEN>`
- `X-Demi-Signature: <hex hmac sha256 body signature>`

Important API groups:

- Client profile: `/api/me/`
- Client bonuses: `/api/me/bonuses/`
- Client orders: `/api/me/orders/`
- Client consultations: `/api/me/consultations/`
- Public catalog: `/api/catalog/categories/`, `/api/catalog/brands/`, `/api/catalog/products/`
- Products: `/api/products/`
- Inventory: `/api/inventory/`
- Sales: `/api/sales/`
- Orders: `/api/orders/`
- Reports: `/api/reports/*.xlsx`
- Auth actions: `/api/auth/logout/`, `/api/auth/password/change/`
- Password reset: `/api/auth/password/reset/`, `/api/auth/password/reset/confirm/`
- Health: `/api/health/`
- Inventory actions: `/api/inventory/stock-movements/receive/`, `/write-off/`, `/transfer/`
- Sales actions: `/api/sales/sales/{id}/complete/`, `/refund/`
- Order actions: `/api/orders/orders/{id}/cancel/`, `/change-status/`
- Payment actions: `/api/payments/payments/{id}/mark-paid/`, `/local/`, `/confirm-local/`, `/fail-local/`, `/refund/`

Swagger groups endpoints with tags such as Products, Inventory, Sales, Orders, Bonuses, AI Assistant and Reports.

Client-facing endpoints use `Me` and `Catalog` tags. They hide staff-only fields such as cost prices, created_by and operational stock movement details.

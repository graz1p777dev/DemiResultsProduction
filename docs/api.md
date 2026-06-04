# API Notes

Swagger is available at `/api/docs/`.

JWT endpoints:

- `POST /api/auth/token/`
- `POST /api/auth/token/refresh/`

n8n endpoint:

- `POST /api/ai/webhook/`

n8n requests must include:

- `Authorization: Token <N8N_API_TOKEN>`
- `X-Demi-Signature: <hex hmac sha256 body signature>`


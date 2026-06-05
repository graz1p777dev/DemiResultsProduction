# Security Notes

Current baseline:

- JWT access and refresh authentication
- Password registration/change/reset uses Django password validators.
- Role-based API permissions
- Environment-based secrets
- CORS origin allow-list
- DRF throttling
- Separate n8n API token
- HMAC signature verification for n8n webhooks
- Audit log model for sensitive actions
- Production settings fail fast when `DJANGO_SECRET_KEY` is unsafe or `ALLOWED_HOSTS` is unrestricted
- n8n webhook uses token comparison and HMAC verification before persisting AI conversation data
- Critical stock, sale, order and bonus operations use service-layer transactions and row locks.
- Kyrgyz phone numbers are validated as `+996123123123`.
- Google OAuth accepts only Google `id_token`; `google_id` is never trusted directly from clients.
- Google token verification checks `GOOGLE_CLIENT_ID` audience and `email_verified`.
- Refresh tokens are blacklisted on logout and after rotation.
- Password reset uses Django signed reset tokens and sends only reset uid/token instructions through the configured email backend.
- Order stock reservations, payment status changes and stock changes use service-layer transactions.
- Phone authentication accepts only Kyrgyz numbers and stores one-time codes as password hashes. With `SMS_PROVIDER=console`, the code is printed to terminal logs for local development.
- Local payment provider does not accept card details and stores only local references such as `LOCAL-...`.
- `GET /api/health/` checks dependencies without returning secrets.

Email env:

- `EMAIL_BACKEND`
- `DEFAULT_FROM_EMAIL`
- `FRONTEND_PASSWORD_RESET_URL`

Required Google env:

- `GOOGLE_CLIENT_ID`

Local SMS env:

- `SMS_PROVIDER=console`
- `PHONE_AUTH_CODE_TTL_MINUTES`

Local payment env:

- `PAYMENT_PROVIDER=local`
- `LOCAL_PAYMENT_AUTO_CAPTURE`

Operations env:

- `BACKUP_DIR`
- `BACKUP_RETENTION_DAYS`
- `LOG_DIR`
- `DJANGO_LOG_LEVEL`

Production checklist:

- Replace all `.env.example` secrets
- Set `DJANGO_DEBUG=false`
- Configure HTTPS at Cloudflare/Nginx
- Restrict admin path or protect admin with VPN/IP allow-list
- Enable database backups
- Configure offsite backup sync outside the app container
- Run Celery worker and Celery Beat
- Add 2FA for owner accounts
- Add object-level permission tests for staff endpoints

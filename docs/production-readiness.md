# Production Readiness

This checklist describes what must be prepared before deploying DemiResults to production.

## Environment

- Set `DJANGO_ENV=production`.
- Set `DJANGO_DEBUG=false`.
- Replace every secret from `.env.example`.
- Use a long random `DJANGO_SECRET_KEY`.
- Restrict `DJANGO_ALLOWED_HOSTS` to real domains.
- Restrict `CORS_ALLOWED_ORIGINS` to frontend/mobile domains.
- Set `DJANGO_CSRF_TRUSTED_ORIGINS` for HTTPS domains.
- Keep `.env` outside git and readable only by the deploy user.

## Server

- Ubuntu VPS with a non-root deploy user.
- Firewall open only for SSH, HTTP and HTTPS.
- SSH keys only; disable password login.
- Docker and Docker Compose installed.
- System updates enabled or scheduled.
- Timezone set correctly.

## Domain And HTTPS

- Domain pointed to the VPS.
- Cloudflare configured for DNS and basic protection.
- HTTPS enabled through Cloudflare/Nginx.
- Nginx reverse proxy configured for Django static/media.
- Production admin URL protected by IP allowlist, VPN, or a non-default path.

## Database

- PostgreSQL data stored on persistent volume.
- Strong database password.
- Regular `pg_dump` backups.
- Backup restore tested on a clean database.
- Offsite backup sync configured, for example S3, Cloudflare R2, or another server.
- Backup retention policy documented.

## Redis And Celery

- Redis persistent enough for Celery needs or acceptable as volatile queue.
- `celery` worker running.
- `celery-beat` running.
- Scheduled tasks verified:
  - report export cleanup
  - database backup
  - backup retention cleanup
  - AI webhook log cleanup
- Worker logs monitored.

## Auth And Security

- JWT lifetimes reviewed.
- Rate limits tuned for:
  - register
  - login
  - phone-code request
  - password reset
  - n8n webhook
- Brute-force lockout added or configured before public launch.
- OWNER 2FA implemented and tested.
- Object-level permissions tested for client data.
- Google OAuth configured with production `GOOGLE_CLIENT_ID`.
- Phone auth connected to real SMS provider.
- Password reset connected to real email provider.

## Payments

- Replace `PAYMENT_PROVIDER=local` with real provider.
- Do not accept raw card data in backend unless PCI requirements are intentionally handled.
- Verify payment webhooks with provider signatures.
- Store provider references, statuses and audit logs.
- Test refund flow.
- Test failed and cancelled payment flow.

## n8n And AI

- Set strong `N8N_API_TOKEN`.
- Set strong `N8N_WEBHOOK_SECRET`.
- Verify HMAC signature on all webhook requests.
- Limit AI assistant permissions to client lookup, catalog search and consultation handoff.
- Log AI requests without storing unnecessary sensitive data.

## Monitoring

- External uptime check for `/api/health/`.
- Error tracking configured, for example Sentry.
- Centralized logs or log shipping configured.
- Disk usage alerts.
- PostgreSQL and Redis health alerts.
- Celery worker availability alerts.

## Release Process

- CI must pass:
  - migrations check
  - Django check
  - tests
  - OpenAPI schema validation
- Run migrations before switching traffic.
- Keep rollback plan ready.
- Tag production releases.
- Do not deploy dirty local-only changes accidentally.

## Final Smoke Test

- `GET /api/health/`
- `GET /api/docs/`
- Register/login client.
- Google login.
- Phone-code login.
- Catalog list/detail.
- Client order create/cancel.
- Staff sale flow.
- Payment create/confirm/refund.
- n8n webhook signed request.
- Excel report export.

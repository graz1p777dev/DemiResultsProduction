# Security Notes

Current baseline:

- JWT access and refresh authentication
- Role-based API permissions
- Environment-based secrets
- CORS origin allow-list
- DRF throttling
- Separate n8n API token
- HMAC signature verification for n8n webhooks
- Audit log model for sensitive actions

Production checklist:

- Replace all `.env.example` secrets
- Set `DJANGO_DEBUG=false`
- Configure HTTPS at Cloudflare/Nginx
- Restrict admin path or protect admin with VPN/IP allow-list
- Enable database backups
- Add 2FA for owner accounts
- Add object-level permission tests for staff endpoints


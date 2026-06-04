from django.utils.deprecation import MiddlewareMixin


class AuditLogMiddleware(MiddlewareMixin):
    WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    def process_response(self, request, response):
        if request.method not in self.WRITE_METHODS:
            return response
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return response
        if not request.path.startswith("/api/"):
            return response

        from apps.audit.models import AuditLog

        AuditLog.objects.create(
            actor=request.user,
            action=f"{request.method} {request.path}",
            entity_type="api_request",
            ip_address=self._get_ip(request),
            user_agent=request.headers.get("User-Agent", ""),
            metadata={"status_code": response.status_code},
        )
        return response

    def _get_ip(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


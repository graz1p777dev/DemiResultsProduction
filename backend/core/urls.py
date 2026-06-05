from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView
from core.views import HealthCheckView
from apps.users.views import (
    GoogleAuthView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PhoneAuthRequestCodeView,
    PhoneAuthVerifyCodeView,
    PhoneEmailTokenObtainPairView,
    RegisterView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/health/", HealthCheckView.as_view(), name="health"),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/token/", PhoneEmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("api/auth/password/reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("api/auth/password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("api/auth/phone/request-code/", PhoneAuthRequestCodeView.as_view(), name="phone_auth_request_code"),
    path("api/auth/phone/verify/", PhoneAuthVerifyCodeView.as_view(), name="phone_auth_verify_code"),
    path("api/auth/google/", GoogleAuthView.as_view(), name="google_auth"),
    path("api/", include("apps.client_api.urls")),
    path("api/users/", include("apps.users.urls")),
    path("api/products/", include("apps.products.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
    path("api/sales/", include("apps.sales.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/delivery/", include("apps.delivery.urls")),
    path("api/bonuses/", include("apps.bonuses.urls")),
    path("api/consultations/", include("apps.consultations.urls")),
    path("api/ai/", include("apps.ai_assistant.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/reports/", include("apps.reports.urls")),
    path("api/audit/", include("apps.audit.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

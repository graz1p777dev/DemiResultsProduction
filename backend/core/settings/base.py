from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = BASE_DIR.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    PHONE_AUTH_CODE_TTL_MINUTES=(int, 5),
    BACKUP_RETENTION_DAYS=(int, 7),
    LOCAL_PAYMENT_AUTO_CAPTURE=(bool, False),
)
environ.Env.read_env(ROOT_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="unsafe-local-dev-key")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "django_filters",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.users",
    "apps.products",
    "apps.inventory",
    "apps.sales",
    "apps.orders",
    "apps.payments",
    "apps.delivery",
    "apps.bonuses",
    "apps.consultations",
    "apps.ai_assistant",
    "apps.notifications",
    "apps.reports",
    "apps.audit",
    "apps.client_api",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "common.middleware.AuditLogMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="demiresults"),
        "USER": env("POSTGRES_USER", default="demiresults"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="demiresults"),
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "PORT": env("POSTGRES_PORT", default="5432"),
    }
}

AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "1000/day",
        "anon": "100/day",
        "n8n": "300/hour",
    },
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "DemiResults API",
    "DESCRIPTION": "Backend API for cosmetics store operations: products, inventory, POS sales, orders, bonuses, consultations, AI assistant and audit.",
    "VERSION": "0.1.0",
    "TAGS": [
        {"name": "Auth", "description": "JWT authentication endpoints."},
        {"name": "Users", "description": "Users, roles and client/staff profiles."},
        {"name": "Products", "description": "Catalog, categories, brands, variants and batches."},
        {"name": "Inventory", "description": "Branches, warehouses, stock levels and stock movements."},
        {"name": "Sales", "description": "POS sales, sale items, returns, totals and profit."},
        {"name": "Orders", "description": "Customer orders, items and status history."},
        {"name": "Payments", "description": "Payments and refunds."},
        {"name": "Delivery", "description": "Addresses, delivery zones and delivery status."},
        {"name": "Bonuses", "description": "Bonus accounts, transactions and promo codes."},
        {"name": "Consultations", "description": "Consultation bookings and messages."},
        {"name": "AI Assistant", "description": "n8n webhook, AI conversations and AI messages."},
        {"name": "Notifications", "description": "In-app, SMS, email and push notifications."},
        {"name": "Reports", "description": "Excel exports for sales, inventory, orders and bonuses."},
        {"name": "Audit", "description": "Read-only audit log for sensitive actions."},
        {"name": "Health", "description": "Dependency health checks."},
        {"name": "Me", "description": "Client-facing profile, orders, bonuses and consultations."},
        {"name": "Catalog", "description": "Public client-facing product catalog."},
    ],
    "ENUM_NAME_OVERRIDES": {
        "OrderStatusEnum": [
            ("CREATED", "Created"),
            ("CONFIRMED", "Confirmed"),
            ("PACKING", "Packing"),
            ("DELIVERING", "Delivering"),
            ("COMPLETED", "Completed"),
            ("CANCELLED", "Cancelled"),
        ],
        "SaleStatusEnum": [
            ("DRAFT", "Draft"),
            ("COMPLETED", "Completed"),
            ("PARTIALLY_REFUNDED", "Partially refunded"),
            ("REFUNDED", "Refunded"),
            ("CANCELLED", "Cancelled"),
        ],
        "DeliveryStatusEnum": [
            ("CREATED", "Created"),
            ("ASSIGNED", "Assigned"),
            ("DELIVERING", "Delivering"),
            ("DELIVERED", "Delivered"),
            ("CANCELLED", "Cancelled"),
        ],
        "PaymentStatusEnum": [
            ("PENDING", "Pending"),
            ("PAID", "Paid"),
            ("FAILED", "Failed"),
            ("REFUNDED", "Refunded"),
        ],
        "ConsultationStatusEnum": [
            ("REQUESTED", "Requested"),
            ("CONFIRMED", "Confirmed"),
            ("COMPLETED", "Completed"),
            ("CANCELLED", "Cancelled"),
        ],
        "StockMovementTypeEnum": [
            ("IN", "Receipt"),
            ("OUT", "Write-off"),
            ("SALE", "Sale"),
            ("RETURN", "Return"),
            ("INVENTORY", "Inventory correction"),
            ("TRANSFER", "Transfer"),
        ],
    },
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

REDIS_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    "cleanup-old-report-exports-daily": {
        "task": "apps.reports.tasks.cleanup_old_report_exports",
        "schedule": 60 * 60 * 24,
        "kwargs": {"days": 30},
    },
    "create-local-database-backup-daily": {
        "task": "apps.reports.tasks.create_database_backup",
        "schedule": 60 * 60 * 24,
    },
    "cleanup-local-database-backups-daily": {
        "task": "apps.reports.tasks.cleanup_old_database_backups",
        "schedule": 60 * 60 * 24,
    },
    "cleanup-invalid-ai-webhook-logs-hourly": {
        "task": "apps.ai_assistant.tasks.cleanup_invalid_webhook_logs",
        "schedule": 60 * 60,
    },
}

N8N_API_TOKEN = env("N8N_API_TOKEN", default="")
N8N_WEBHOOK_SECRET = env("N8N_WEBHOOK_SECRET", default="")

GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default="")

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="DemiResults <noreply@demiresults.local>")
FRONTEND_PASSWORD_RESET_URL = env("FRONTEND_PASSWORD_RESET_URL", default="")

SMS_PROVIDER = env("SMS_PROVIDER", default="console")
PHONE_AUTH_CODE_TTL_MINUTES = env("PHONE_AUTH_CODE_TTL_MINUTES")

PAYMENT_PROVIDER = env("PAYMENT_PROVIDER", default="local")
LOCAL_PAYMENT_AUTO_CAPTURE = env("LOCAL_PAYMENT_AUTO_CAPTURE")

BACKUP_DIR = env("BACKUP_DIR", default=str(BASE_DIR / "backups"))
BACKUP_RETENTION_DAYS = env("BACKUP_RETENTION_DAYS")
LOG_DIR = Path(env("LOG_DIR", default=str(BASE_DIR / "logs")))
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "demiresults.log",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "standard",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": env("DJANGO_LOG_LEVEL", default="INFO"),
    },
}

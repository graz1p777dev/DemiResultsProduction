from dataclasses import dataclass
import logging
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework_simplejwt.tokens import RefreshToken

from .models import ClientProfile, PhoneAuthCode

logger = logging.getLogger(__name__)


class GoogleAuthErrorBase(Exception):
    default_code = "google_auth_error"


class GoogleTokenInvalid(GoogleAuthErrorBase):
    default_code = "invalid_google_token"


class GoogleAudienceMismatch(GoogleAuthErrorBase):
    default_code = "google_audience_mismatch"


class GoogleEmailNotVerified(GoogleAuthErrorBase):
    default_code = "google_email_not_verified"


class GoogleAuthServiceUnavailable(GoogleAuthErrorBase):
    default_code = "google_auth_service_unavailable"


class PhoneAuthError(Exception):
    default_code = "phone_auth_error"


class PhoneCodeInvalid(PhoneAuthError):
    default_code = "invalid_phone_code"


class PhoneCodeExpired(PhoneAuthError):
    default_code = "expired_phone_code"


class PhoneCodeTooManyAttempts(PhoneAuthError):
    default_code = "too_many_phone_code_attempts"


@dataclass
class GoogleAuthResult:
    user: object
    access: str
    refresh: str


def verify_google_id_token(id_token: str):
    if not settings.GOOGLE_CLIENT_ID:
        raise GoogleAuthServiceUnavailable("GOOGLE_CLIENT_ID is not configured.")
    try:
        payload = google_id_token.verify_oauth2_token(
            id_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        message = str(exc).lower()
        if "audience" in message or "wrong recipient" in message:
            raise GoogleAudienceMismatch("Google token audience does not match this backend.") from exc
        raise GoogleTokenInvalid("Invalid Google id_token.") from exc
    except GoogleAuthError as exc:
        raise GoogleAuthServiceUnavailable("Google token verification is temporarily unavailable.") from exc

    if payload.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise GoogleAudienceMismatch("Google token audience does not match this backend.")
    if not payload.get("email_verified"):
        raise GoogleEmailNotVerified("Google email is not verified.")
    return payload


@transaction.atomic
def get_or_create_google_user(google_payload):
    User = get_user_model()
    google_sub = google_payload["sub"]
    email = google_payload["email"].lower()

    user = User.objects.select_for_update().filter(google_id=google_sub).first()
    if not user:
        user = User.objects.select_for_update().filter(email__iexact=email).first()
        if user:
            user.google_id = google_sub
            user.save(update_fields=["google_id"])
    if not user:
        base_username = email.split("@", 1)[0]
        username = base_username
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base_username}{suffix}"
        user = User.objects.create_user(
            username=username,
            email=email,
            google_id=google_sub,
            first_name=google_payload.get("given_name", ""),
            last_name=google_payload.get("family_name", ""),
            role=User.Role.CLIENT,
        )
        user.set_unusable_password()
        user.save(update_fields=["password"])

    profile, _ = ClientProfile.objects.get_or_create(user=user)
    return user


def build_user_payload(user):
    return {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "has_client_profile": hasattr(user, "client_profile"),
    }


def login_with_google(id_token: str):
    payload = verify_google_id_token(id_token)
    user = get_or_create_google_user(payload)
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": build_user_payload(user),
    }


def _issue_jwt_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": build_user_payload(user),
    }


def _generate_phone_code():
    return f"{random.SystemRandom().randint(0, 999999):06d}"


def send_sms_code(*, phone: str, code: str):
    provider = settings.SMS_PROVIDER
    if provider != "console":
        logger.warning("Unsupported SMS_PROVIDER=%s. Falling back to console provider.", provider)
    # This is intentionally visible in Docker/Celery logs for local development.
    logger.info("DemiResults SMS code for %s: %s", phone, code)
    print(f"DemiResults SMS code for {phone}: {code}", flush=True)


@transaction.atomic
def request_phone_login_code(phone: str):
    code = _generate_phone_code()
    now = timezone.now()
    expires_at = now + timezone.timedelta(minutes=settings.PHONE_AUTH_CODE_TTL_MINUTES)
    PhoneAuthCode.objects.filter(
        phone=phone,
        purpose=PhoneAuthCode.Purpose.LOGIN,
        consumed_at__isnull=True,
    ).update(consumed_at=now)
    PhoneAuthCode.objects.create(
        phone=phone,
        code_hash=make_password(code),
        purpose=PhoneAuthCode.Purpose.LOGIN,
        expires_at=expires_at,
    )
    send_sms_code(phone=phone, code=code)
    return {"expires_at": expires_at}


@transaction.atomic
def verify_phone_login_code(*, phone: str, code: str):
    auth_code = (
        PhoneAuthCode.objects.select_for_update()
        .filter(phone=phone, purpose=PhoneAuthCode.Purpose.LOGIN, consumed_at__isnull=True)
        .order_by("-created_at")
        .first()
    )
    if not auth_code:
        raise PhoneCodeInvalid("Invalid phone code.")
    if auth_code.attempts >= auth_code.max_attempts:
        raise PhoneCodeTooManyAttempts("Too many phone code attempts.")
    if auth_code.is_expired:
        auth_code.consumed_at = timezone.now()
        auth_code.save(update_fields=["consumed_at"])
        raise PhoneCodeExpired("Phone code has expired.")
    auth_code.attempts += 1
    if not check_password(code, auth_code.code_hash):
        auth_code.save(update_fields=["attempts"])
        raise PhoneCodeInvalid("Invalid phone code.")

    auth_code.consumed_at = timezone.now()
    auth_code.save(update_fields=["attempts", "consumed_at"])
    User = get_user_model()
    user = User.objects.select_for_update().filter(phone=phone).first()
    if not user:
        username_base = phone.replace("+", "")
        username = username_base
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{username_base}{suffix}"
        user = User.objects.create_user(username=username, email=f"{username}@phone.demiresults.local", phone=phone, role=User.Role.CLIENT)
        user.set_unusable_password()
        user.save(update_fields=["password"])
    ClientProfile.objects.get_or_create(user=user)
    return _issue_jwt_for_user(user)


def request_password_reset(email: str):
    User = get_user_model()
    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if not user:
        return None
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = f"{settings.FRONTEND_PASSWORD_RESET_URL}?uid={uid}&token={token}" if settings.FRONTEND_PASSWORD_RESET_URL else ""
    message = (
        "Use this password reset token for DemiResults.\n"
        f"uid: {uid}\n"
        f"token: {token}\n"
    )
    if reset_url:
        message += f"reset_url: {reset_url}\n"
    send_mail(
        subject="DemiResults password reset",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return {"uid": uid}


def confirm_password_reset(*, uid, token, new_password):
    User = get_user_model()
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id, is_active=True)
    except (User.DoesNotExist, ValueError, TypeError):
        raise GoogleTokenInvalid("Invalid password reset token.")
    if not default_token_generator.check_token(user, token):
        raise GoogleTokenInvalid("Invalid password reset token.")
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return user

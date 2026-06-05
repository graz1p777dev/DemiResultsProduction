from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.users.models import ClientProfile
from apps.users import auth_services


GOOGLE_PAYLOAD = {
    "sub": "google-sub-1",
    "email": "client@example.com",
    "email_verified": True,
    "given_name": "Ainara",
    "family_name": "T",
    "picture": "https://example.com/avatar.jpg",
    "aud": "google-client-id",
}


@pytest.mark.django_db
@patch("apps.users.auth_services.verify_google_id_token")
def test_google_login_creates_new_user(mock_verify, settings):
    settings.GOOGLE_CLIENT_ID = "google-client-id"
    mock_verify.return_value = GOOGLE_PAYLOAD

    response = APIClient().post("/api/auth/google/", {"id_token": "valid-token"}, format="json")

    assert response.status_code == 200
    user = get_user_model().objects.get(email="client@example.com")
    assert user.google_id == "google-sub-1"
    assert user.role == get_user_model().Role.CLIENT
    assert not user.has_usable_password()


@pytest.mark.django_db
@patch("apps.users.auth_services.verify_google_id_token")
def test_google_login_links_existing_user_by_email(mock_verify, settings):
    settings.GOOGLE_CLIENT_ID = "google-client-id"
    user = get_user_model().objects.create_user(username="existing", email="client@example.com", password="pass12345")
    mock_verify.return_value = GOOGLE_PAYLOAD

    response = APIClient().post("/api/auth/google/", {"id_token": "valid-token"}, format="json")
    user.refresh_from_db()

    assert response.status_code == 200
    assert user.google_id == "google-sub-1"
    assert get_user_model().objects.filter(email="client@example.com").count() == 1


@pytest.mark.django_db
@patch("apps.users.auth_services.verify_google_id_token")
def test_google_login_returns_jwt_tokens_and_user_payload(mock_verify, settings):
    settings.GOOGLE_CLIENT_ID = "google-client-id"
    mock_verify.return_value = GOOGLE_PAYLOAD

    response = APIClient().post("/api/auth/google/", {"id_token": "valid-token"}, format="json")

    assert response.status_code == 200
    assert response.data["access"]
    assert response.data["refresh"]
    assert response.data["user"]["email"] == "client@example.com"
    assert response.data["user"]["has_client_profile"] is True


@pytest.mark.django_db
@patch("apps.users.auth_services.verify_google_id_token")
def test_google_login_rejects_unverified_email(mock_verify, settings):
    settings.GOOGLE_CLIENT_ID = "google-client-id"
    mock_verify.side_effect = auth_services.GoogleEmailNotVerified("Google email is not verified.")

    response = APIClient().post("/api/auth/google/", {"id_token": "valid-token"}, format="json")

    assert response.status_code == 400
    assert response.data["code"] == "google_email_not_verified"


@pytest.mark.django_db
@patch("apps.users.auth_services.verify_google_id_token")
def test_google_login_rejects_invalid_token(mock_verify, settings):
    settings.GOOGLE_CLIENT_ID = "google-client-id"
    mock_verify.side_effect = auth_services.GoogleTokenInvalid("Invalid Google id_token.")

    response = APIClient().post("/api/auth/google/", {"id_token": "bad-token"}, format="json")

    assert response.status_code == 401
    assert response.data["code"] == "invalid_google_token"


@pytest.mark.django_db
@patch("apps.users.auth_services.verify_google_id_token")
def test_google_login_creates_client_profile(mock_verify, settings):
    settings.GOOGLE_CLIENT_ID = "google-client-id"
    mock_verify.return_value = GOOGLE_PAYLOAD

    response = APIClient().post("/api/auth/google/", {"id_token": "valid-token"}, format="json")
    user = get_user_model().objects.get(email="client@example.com")

    assert response.status_code == 200
    assert ClientProfile.objects.filter(user=user).exists()


@pytest.mark.django_db
@patch("apps.users.auth_services.verify_google_id_token")
def test_google_login_does_not_require_password(mock_verify, settings):
    settings.GOOGLE_CLIENT_ID = "google-client-id"
    mock_verify.return_value = GOOGLE_PAYLOAD

    response = APIClient().post("/api/auth/google/", {"id_token": "valid-token"}, format="json")
    user = get_user_model().objects.get(email="client@example.com")

    assert response.status_code == 200
    assert not user.has_usable_password()


@pytest.mark.django_db
def test_telegram_is_not_used_in_auth_flow():
    response = APIClient().post("/api/auth/google/", {"telegram_username": "client"}, format="json")

    assert response.status_code == 400
    assert "id_token" in response.data


@pytest.mark.django_db
def test_password_login_accepts_email_or_phone():
    user = get_user_model().objects.create_user(
        username="password-client",
        email="password-client@example.com",
        phone="+996700111222",
        password="pass12345",
    )
    client = APIClient()

    email_response = client.post("/api/auth/token/", {"username": user.email, "password": "pass12345"}, format="json")
    phone_response = client.post("/api/auth/token/", {"username": user.phone, "password": "pass12345"}, format="json")

    assert email_response.status_code == 200
    assert phone_response.status_code == 200
    assert email_response.data["access"]
    assert phone_response.data["refresh"]

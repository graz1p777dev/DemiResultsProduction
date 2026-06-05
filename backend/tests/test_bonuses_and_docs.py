import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.bonuses import services as bonus_service

from .factories import make_user


@pytest.mark.django_db
def test_bonus_accrue_spend_and_rollback():
    client = make_user("bonus-client", role="CLIENT")
    manager = make_user("bonus-manager", role="MANAGER")

    accrual = bonus_service.accrue_bonus(client=client, amount="100.00", created_by=manager)
    spend = bonus_service.spend_bonus(client=client, amount="40.00", created_by=manager)
    account = client.bonus_account
    account.refresh_from_db()

    assert account.balance == 60

    bonus_service.rollback_bonus(transaction=spend, created_by=manager)
    account.refresh_from_db()

    assert account.balance == 100
    assert accrual.amount == 100


@pytest.mark.django_db
def test_bonus_spend_more_than_balance_is_forbidden():
    client = make_user("bonus-low-client", role="CLIENT")

    with pytest.raises(ValidationError):
        bonus_service.spend_bonus(client=client, amount="1.00")


@pytest.mark.django_db
def test_schema_docs_and_redoc_are_available():
    client = APIClient()

    assert client.get("/api/schema/").status_code == 200
    assert client.get("/api/docs/").status_code == 200
    assert client.get("/api/redoc/").status_code == 200

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import status

from app.core.paypal_client import PayPalClient
from app.dependencies import get_paypal_client
from app.models.order import Order, OrderStatus
from main import app


def create_order(db, *, user_id: int, total: Decimal = Decimal("40.00")) -> Order:
    order = Order(user_id=user_id, total_amount=total, currency="USD", status=OrderStatus.PENDING)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@pytest.fixture()
def paypal_client_mock():
    mock = MagicMock(spec=PayPalClient)
    mock.create_order.return_value = {
        "id": "PAYPAL-ORDER",
        "links": [{"rel": "approve", "href": "https://paypal.test/approve"}],
    }
    mock.capture_order.return_value = {"status": "COMPLETED"}
    return mock


@pytest.fixture(autouse=True)
def override_paypal_client(paypal_client_mock):
    app.dependency_overrides[get_paypal_client] = lambda: paypal_client_mock
    yield
    app.dependency_overrides.pop(get_paypal_client, None)


def test_create_paypal_order_requires_auth(client):
    response = client.post(
        "/api/v1/payments/paypal/create",
        json={"order_id": 1},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_paypal_order_only_for_owner(
    client,
    create_buyer,
    db_session,
    auth_header_factory,
):
    owner = create_buyer(email="owner@example.com")
    stranger = create_buyer(email="stranger@example.com")
    order = create_order(db_session, user_id=owner.id)

    response = client.post(
        "/api/v1/payments/paypal/create",
        headers=auth_header_factory(stranger),
        json={"order_id": order.id},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_capture_paypal_order_requires_auth(client):
    response = client.post(
        "/api/v1/payments/paypal/capture",
        json={"provider_payment_id": "abc"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_and_capture_full_flow(
    client,
    create_buyer,
    db_session,
    auth_header_factory,
    paypal_client_mock,
):
    buyer = create_buyer()
    order = create_order(db_session, user_id=buyer.id)
    headers = auth_header_factory(buyer)

    create_response = client.post(
        "/api/v1/payments/paypal/create",
        headers=headers,
        json={"order_id": order.id},
    )

    assert create_response.status_code == status.HTTP_200_OK
    body = create_response.json()
    assert body["provider_payment_id"] == "PAYPAL-ORDER"

    capture_response = client.post(
        "/api/v1/payments/paypal/capture",
        headers=headers,
        json={"provider_payment_id": body["provider_payment_id"]},
    )

    assert capture_response.status_code == status.HTTP_200_OK
    capture_body = capture_response.json()
    assert capture_body["status"] == "COMPLETED"
    assert capture_body["order_status"] == OrderStatus.PAID.value

    db_session.refresh(order)
    assert order.status == OrderStatus.PAID

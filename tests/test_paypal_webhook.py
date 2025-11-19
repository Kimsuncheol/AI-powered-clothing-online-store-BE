from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import status

from app.core.paypal_client import PayPalClient
from app.dependencies import get_paypal_client
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.models.paypal_event import PayPalEvent
from main import app


def create_order(db, *, user_id: int) -> Order:
    order = Order(
        user_id=user_id,
        total_amount=Decimal("55.00"),
        currency="USD",
        status=OrderStatus.PENDING,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def create_payment(db, *, order_id: int, provider_payment_id: str) -> Payment:
    payment = Payment(
        order_id=order_id,
        provider_payment_id=provider_payment_id,
        status=PaymentStatus.CREATED,
        raw_response={"status": "CREATED"},
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@pytest.fixture(autouse=True)
def override_paypal_client():
    mock = MagicMock(spec=PayPalClient)
    app.dependency_overrides[get_paypal_client] = lambda: mock
    yield
    app.dependency_overrides.pop(get_paypal_client, None)


def test_webhook_saves_new_event_and_is_idempotent(
    client,
    db_session,
):
    payload = {
        "id": "evt-1",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource": {"id": "PAYPAL-1", "status": "COMPLETED"},
    }

    response = client.post("/api/v1/payments/paypal/webhook", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    first_count = db_session.query(PayPalEvent).count()
    assert first_count == 1

    response = client.post("/api/v1/payments/paypal/webhook", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    second_count = db_session.query(PayPalEvent).count()
    assert second_count == 1


def test_webhook_updates_payment_status_on_capture_completed(
    client,
    db_session,
    create_buyer,
):
    buyer = create_buyer()
    order = create_order(db_session, user_id=buyer.id)
    payment = create_payment(db_session, order_id=order.id, provider_payment_id="PAYPAL-CAPTURE")
    payload = {
        "id": "evt-2",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource": {
            "id": "PAYPAL-CAPTURE",
            "status": "COMPLETED",
            "supplementary_data": {"related_ids": {"order_id": "PAYPAL-CAPTURE"}},
        },
    }

    response = client.post("/api/v1/payments/paypal/webhook", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db_session.refresh(payment)
    db_session.refresh(order)
    assert payment.status == PaymentStatus.COMPLETED
    assert order.status == OrderStatus.PAID

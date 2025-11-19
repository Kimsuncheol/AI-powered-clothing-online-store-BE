from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status

from app.core.paypal_client import PayPalClient
from app.models.order import Order, OrderStatus
from app.models.payment import PaymentStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.paypal_event_repository import PayPalEventRepository
from app.services.payment_service import PaymentService


def create_order(db, *, user_id: int, total: Decimal = Decimal("50.00"), status_: OrderStatus = OrderStatus.PENDING) -> Order:
    order = Order(user_id=user_id, total_amount=total, currency="USD", status=status_)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@pytest.fixture()
def paypal_client_mock():
    return MagicMock(spec=PayPalClient)


@pytest.fixture()
def payment_service(paypal_client_mock):
    return PaymentService(
        PaymentRepository(),
        OrderRepository(),
        paypal_client_mock,
        PayPalEventRepository(),
    )


def test_create_paypal_order_validates_order_and_creates_payment(
    db_session,
    create_buyer,
    payment_service,
    paypal_client_mock,
):
    buyer = create_buyer()
    order = create_order(db_session, user_id=buyer.id)
    paypal_client_mock.create_order.return_value = {
        "id": "PAYPAL123",
        "links": [{"rel": "approve", "href": "https://paypal.test/approve"}],
    }

    payment, approval_url = payment_service.create_paypal_order(
        db_session,
        order_id=order.id,
        user_id=buyer.id,
    )

    assert payment.status == PaymentStatus.CREATED
    assert approval_url == "https://paypal.test/approve"
    paypal_client_mock.create_order.assert_called_once()


def test_create_paypal_order_fails_for_invalid_order_status(
    db_session,
    create_buyer,
    payment_service,
    paypal_client_mock,
):
    buyer = create_buyer()
    order = create_order(
        db_session,
        user_id=buyer.id,
        status_=OrderStatus.PAID,
    )

    with pytest.raises(HTTPException) as exc:
        payment_service.create_paypal_order(
            db_session,
            order_id=order.id,
            user_id=buyer.id,
        )

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    paypal_client_mock.create_order.assert_not_called()


def test_capture_paypal_order_updates_statuses_on_success(
    db_session,
    create_buyer,
    payment_service,
    paypal_client_mock,
):
    buyer = create_buyer()
    order = create_order(db_session, user_id=buyer.id)
    payment = payment_service.payment_repo.create_payment(
        db_session,
        order_id=order.id,
        provider_payment_id="PAYPAL456",
        raw_response={"status": "CREATED"},
    )
    paypal_client_mock.capture_order.return_value = {"status": "COMPLETED"}

    updated_payment = payment_service.capture_paypal_order(
        db_session,
        provider_payment_id=payment.provider_payment_id,
        user_id=buyer.id,
    )

    assert updated_payment.status == PaymentStatus.COMPLETED
    assert updated_payment.order.status == OrderStatus.PAID


def test_capture_paypal_order_sets_failed_on_error(
    db_session,
    create_buyer,
    payment_service,
    paypal_client_mock,
):
    buyer = create_buyer()
    order = create_order(db_session, user_id=buyer.id)
    payment = payment_service.payment_repo.create_payment(
        db_session,
        order_id=order.id,
        provider_payment_id="PAYPAL789",
        raw_response={"status": "CREATED"},
    )
    paypal_client_mock.capture_order.return_value = {"status": "FAILED"}

    with pytest.raises(HTTPException) as exc:
        payment_service.capture_paypal_order(
            db_session,
            provider_payment_id=payment.provider_payment_id,
            user_id=buyer.id,
        )

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    refreshed_payment = payment_service.payment_repo.get_by_provider_payment_id(
        db_session,
        provider_payment_id="PAYPAL789",
    )
    assert refreshed_payment.status == PaymentStatus.FAILED

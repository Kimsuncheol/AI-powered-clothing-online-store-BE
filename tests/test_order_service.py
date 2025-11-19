from decimal import Decimal

import pytest
from fastapi import HTTPException, status

from app.models.order import Order
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartItemCreate
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from tests.conftest import create_product


@pytest.fixture()
def cart_service():
    return CartService(CartRepository(), ProductRepository())


@pytest.fixture()
def order_service():
    return OrderService(CartRepository(), OrderRepository(), ProductRepository())


def test_create_order_from_cart_computes_total_correctly(
    db_session,
    create_buyer,
    create_seller,
    cart_service,
    order_service,
):
    buyer = create_buyer()
    seller = create_seller()
    product_one = create_product(
        db_session,
        seller_id=seller.id,
        price=Decimal("10.00"),
    )
    product_two = create_product(
        db_session,
        seller_id=seller.id,
        price=Decimal("25.00"),
    )

    cart_service.add_item_to_cart(
        db_session,
        buyer.id,
        CartItemCreate(product_id=product_one.id, quantity=2),
    )
    cart_service.add_item_to_cart(
        db_session,
        buyer.id,
        CartItemCreate(product_id=product_two.id, quantity=1),
    )

    order_response = order_service.create_order_from_cart(db_session, buyer.id)

    assert order_response.total_amount == Decimal("45.00")

    created_order = db_session.query(Order).first()
    assert created_order is not None
    assert len(created_order.items) == 2


def test_create_order_reduces_stock_if_implemented(
    db_session,
    create_buyer,
    create_seller,
    cart_service,
    order_service,
):
    buyer = create_buyer()
    seller = create_seller()
    product = create_product(
        db_session,
        seller_id=seller.id,
        price=Decimal("15.00"),
        stock=5,
    )

    cart_service.add_item_to_cart(
        db_session,
        buyer.id,
        CartItemCreate(product_id=product.id, quantity=2),
    )

    order_service.create_order_from_cart(db_session, buyer.id)
    db_session.refresh(product)

    assert product.stock == 3


def test_get_order_detail_for_user_raises_if_not_owner(
    db_session,
    create_buyer,
    create_seller,
    cart_service,
    order_service,
):
    owner = create_buyer(email="owner@example.com")
    other_user = create_buyer(email="other@example.com")
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id)

    cart_service.add_item_to_cart(
        db_session,
        owner.id,
        CartItemCreate(product_id=product.id, quantity=1),
    )
    order_service.create_order_from_cart(db_session, owner.id)
    order = db_session.query(Order).first()

    with pytest.raises(HTTPException) as exc:
        order_service.get_order_detail_for_user(
            db_session,
            other_user.id,
            order.id,
        )

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

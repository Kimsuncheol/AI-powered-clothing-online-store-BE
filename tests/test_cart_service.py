import pytest
from fastapi import HTTPException, status

from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartItemCreate
from app.services.cart_service import CartService
from tests.conftest import create_product


@pytest.fixture()
def cart_service():
    return CartService(CartRepository(), ProductRepository())


def test_add_item_to_cart_fails_for_invalid_product(
    db_session,
    create_buyer,
    cart_service,
):
    buyer = create_buyer()

    with pytest.raises(HTTPException) as exc:
        cart_service.add_item_to_cart(
            db_session,
            buyer.id,
            CartItemCreate(product_id=999, quantity=1),
        )

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_add_item_to_cart_accumulates_quantity_if_same_product(
    db_session,
    create_buyer,
    create_seller,
    cart_service,
):
    buyer = create_buyer()
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id)

    cart_service.add_item_to_cart(
        db_session,
        buyer.id,
        CartItemCreate(product_id=product.id, quantity=2),
    )
    cart = cart_service.add_item_to_cart(
        db_session,
        buyer.id,
        CartItemCreate(product_id=product.id, quantity=3),
    )

    assert cart.items[0].quantity == 5


def test_update_cart_item_quantity_checks_ownership(
    db_session,
    create_buyer,
    create_seller,
    cart_service,
):
    owner = create_buyer(email="owner@example.com")
    intruder = create_buyer(email="intruder@example.com")
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id)

    cart = cart_service.add_item_to_cart(
        db_session,
        owner.id,
        CartItemCreate(product_id=product.id, quantity=1),
    )
    item_id = cart.items[0].id

    with pytest.raises(HTTPException) as exc:
        cart_service.update_cart_item_quantity(db_session, intruder.id, item_id, 2)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_remove_cart_item_checks_ownership(
    db_session,
    create_buyer,
    create_seller,
    cart_service,
):
    owner = create_buyer(email="owner2@example.com")
    other_user = create_buyer(email="other@example.com")
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id)

    cart = cart_service.add_item_to_cart(
        db_session,
        owner.id,
        CartItemCreate(product_id=product.id, quantity=1),
    )
    item_id = cart.items[0].id

    with pytest.raises(HTTPException) as exc:
        cart_service.remove_cart_item(db_session, other_user.id, item_id)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND

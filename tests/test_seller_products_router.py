from decimal import Decimal

from fastapi import status

from app.models.product import ProductStatus
from tests.conftest import create_product


def test_seller_can_create_product(
    client,
    create_seller,
    auth_header_factory,
):
    seller = create_seller()
    payload = {
        "name": "Jacket",
        "description": "Warm",
        "price": "120.00",
        "category": "outerwear",
        "gender": "unisex",
        "size_options": ["M", "L"],
        "color_options": ["black"],
        "variants": {"length": "regular"},
        "stock": 5,
        "images": [{"url": "http://img", "is_avatar_preview": True}],
        "avatar_configs": [{"avatar_preset_id": 2}],
    }

    response = client.post(
        "/api/v1/seller/products",
        json=payload,
        headers=auth_header_factory(seller),
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["name"] == "Jacket"
    assert body["seller"]["id"] == seller.id


def test_non_seller_cannot_create_product(
    client,
    create_buyer,
    auth_header_factory,
):
    buyer = create_buyer()
    payload = {
        "name": "Sneakers",
        "price": "50.00",
        "stock": 3,
    }
    response = client.post(
        "/api/v1/seller/products",
        json=payload,
        headers=auth_header_factory(buyer),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_seller_can_update_own_product(
    client,
    db_session,
    create_seller,
    auth_header_factory,
):
    seller = create_seller()
    product = create_product(
        db_session,
        seller_id=seller.id,
        price=Decimal("10.00"),
    )

    response = client.patch(
        f"/api/v1/seller/products/{product.id}",
        json={"price": "25.00", "name": "Updated"},
        headers=auth_header_factory(seller),
    )

    assert response.status_code == status.HTTP_200_OK
    assert Decimal(str(response.json()["price"])) == Decimal("25.00")


def test_seller_cannot_update_others_product(
    client,
    db_session,
    create_seller,
    auth_header_factory,
):
    seller_one = create_seller(email="seller1@example.com")
    seller_two = create_seller(email="seller2@example.com")
    product = create_product(db_session, seller_id=seller_one.id)

    response = client.patch(
        f"/api/v1/seller/products/{product.id}",
        json={"name": "Hack"},
        headers=auth_header_factory(seller_two),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_seller_soft_delete_marks_status_deleted(
    client,
    db_session,
    create_seller,
    auth_header_factory,
):
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id)

    response = client.delete(
        f"/api/v1/seller/products/{product.id}",
        headers=auth_header_factory(seller),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    db_session.refresh(product)
    assert product.status == ProductStatus.DELETED

    detail_response = client.get(f"/api/v1/products/{product.id}")
    assert detail_response.status_code == status.HTTP_404_NOT_FOUND

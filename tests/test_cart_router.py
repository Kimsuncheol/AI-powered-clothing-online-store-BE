from decimal import Decimal

from fastapi import status

from tests.conftest import create_product


def test_get_cart_returns_empty_cart_for_new_user(
    client,
    create_buyer,
    auth_header_factory,
):
    buyer = create_buyer()
    headers = auth_header_factory(buyer)

    response = client.get("/api/v1/cart", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["items"] == []


def test_add_item_creates_cart_and_adds_item(
    client,
    create_buyer,
    create_seller,
    auth_header_factory,
    db_session,
):
    buyer = create_buyer()
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id, price=Decimal("20.00"))
    headers = auth_header_factory(buyer)

    response = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": product.id, "quantity": 2},
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 2


def test_update_cart_item_changes_quantity(
    client,
    create_buyer,
    create_seller,
    auth_header_factory,
    db_session,
):
    buyer = create_buyer()
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id)
    headers = auth_header_factory(buyer)
    create_resp = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": product.id, "quantity": 1},
    )
    item_id = create_resp.json()["items"][0]["id"]

    response = client.patch(
        f"/api/v1/cart/items/{item_id}",
        headers=headers,
        json={"quantity": 5},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["items"][0]["quantity"] == 5


def test_delete_cart_item_removes_item(
    client,
    create_buyer,
    create_seller,
    auth_header_factory,
    db_session,
):
    buyer = create_buyer()
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id)
    headers = auth_header_factory(buyer)
    create_resp = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": product.id, "quantity": 1},
    )
    item_id = create_resp.json()["items"][0]["id"]

    delete_resp = client.delete(f"/api/v1/cart/items/{item_id}", headers=headers)

    assert delete_resp.status_code == status.HTTP_200_OK
    assert delete_resp.json()["items"] == []


def test_cart_endpoints_require_authentication(client):
    response = client.get("/api/v1/cart")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

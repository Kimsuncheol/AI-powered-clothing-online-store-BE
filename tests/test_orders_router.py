from decimal import Decimal

from fastapi import status

from tests.conftest import create_product


def add_item(client, headers, product_id, quantity=1):
    response = client.post(
        "/api/v1/cart/items",
        headers=headers,
        json={"product_id": product_id, "quantity": quantity},
    )
    assert response.status_code in {status.HTTP_200_OK, status.HTTP_201_CREATED}


def test_create_order_from_cart_creates_order_and_clears_cart(
    client,
    create_buyer,
    create_seller,
    auth_header_factory,
    db_session,
):
    buyer = create_buyer()
    seller = create_seller()
    product = create_product(
        db_session,
        seller_id=seller.id,
        price=Decimal("30.00"),
    )
    headers = auth_header_factory(buyer)
    add_item(client, headers, product.id, 2)

    order_response = client.post("/api/v1/orders", headers=headers)

    assert order_response.status_code == status.HTTP_201_CREATED
    body = order_response.json()
    assert body["total_amount"] == "60.00"

    cart_response = client.get("/api/v1/cart", headers=headers)
    assert cart_response.json()["items"] == []


def test_create_order_fails_when_stock_insufficient(
    client,
    create_buyer,
    create_seller,
    auth_header_factory,
    db_session,
):
    buyer = create_buyer()
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id, stock=1)
    headers = auth_header_factory(buyer)
    add_item(client, headers, product.id, 2)

    response = client.post("/api/v1/orders", headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_order_detail_only_allows_owner(
    client,
    create_buyer,
    create_seller,
    auth_header_factory,
    db_session,
):
    owner = create_buyer(email="owner@example.com")
    other_user = create_buyer(email="other@example.com")
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id)

    owner_headers = auth_header_factory(owner)
    other_headers = auth_header_factory(other_user)
    add_item(client, owner_headers, product.id, 1)
    order_response = client.post("/api/v1/orders", headers=owner_headers)
    order_id = order_response.json()["id"]

    response = client.get(f"/api/v1/orders/{order_id}", headers=other_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_orders_returns_only_current_user_orders(
    client,
    create_buyer,
    create_seller,
    auth_header_factory,
    db_session,
):
    buyer_one = create_buyer(email="buyer1@example.com")
    buyer_two = create_buyer(email="buyer2@example.com")
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id)

    headers_one = auth_header_factory(buyer_one)
    headers_two = auth_header_factory(buyer_two)

    add_item(client, headers_one, product.id, 1)
    client.post("/api/v1/orders", headers=headers_one)
    add_item(client, headers_one, product.id, 1)
    client.post("/api/v1/orders", headers=headers_one)

    add_item(client, headers_two, product.id, 1)
    client.post("/api/v1/orders", headers=headers_two)

    response = client.get("/api/v1/orders", headers=headers_one)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 2

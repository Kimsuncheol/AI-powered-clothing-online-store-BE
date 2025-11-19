from decimal import Decimal

from fastapi import status

from app.models.product import ProductStatus
from tests.conftest import create_product


def test_list_products_returns_paginated_results(client, db_session, create_seller):
    seller = create_seller()
    for i in range(3):
        create_product(
            db_session,
            seller_id=seller.id,
            name=f"Product {i}",
            price=Decimal("10.00") + i,
        )

    response = client.get("/api/v1/products", params={"page": 1, "page_size": 2})

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2


def test_list_products_filters_by_category_and_price(client, db_session, create_seller):
    seller = create_seller()
    create_product(
        db_session,
        seller_id=seller.id,
        category="tops",
        price=Decimal("25.00"),
    )
    create_product(
        db_session,
        seller_id=seller.id,
        category="bottoms",
        price=Decimal("50.00"),
    )

    response = client.get(
        "/api/v1/products",
        params={"category": "tops", "price_max": "30"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["category"] == "tops"


def test_list_products_respects_sorting_newest_and_price(client, db_session, create_seller):
    seller = create_seller()
    cheaper = create_product(
        db_session,
        seller_id=seller.id,
        name="Cheap",
        price=Decimal("10.00"),
    )
    pricy = create_product(
        db_session,
        seller_id=seller.id,
        name="Expensive",
        price=Decimal("100.00"),
    )

    response = client.get("/api/v1/products", params={"sort": "price_desc"})
    assert response.status_code == status.HTTP_200_OK
    items = response.json()["items"]
    assert items[0]["id"] == pricy.id

    response = client.get("/api/v1/products", params={"sort": "price_asc"})
    assert response.json()["items"][0]["id"] == cheaper.id


def test_get_product_detail_includes_seller_and_images_and_avatar_configs(
    client,
    db_session,
    create_seller,
):
    seller = create_seller()
    product = create_product(
        db_session,
        seller_id=seller.id,
        images=[{"url": "https://example.com/image.jpg"}],
        avatar_configs=[{"avatar_preset_id": 1, "style_params": {"color": "red"}}],
    )

    response = client.get(f"/api/v1/products/{product.id}")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["seller"]["email"] == seller.email
    assert len(body["images"]) == 1
    assert len(body["avatar_configs"]) == 1


def test_get_product_detail_returns_404_for_deleted_product(
    client,
    db_session,
    create_seller,
):
    seller = create_seller()
    product = create_product(
        db_session,
        seller_id=seller.id,
        status=ProductStatus.DELETED,
    )

    response = client.get(f"/api/v1/products/{product.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

from app.models.product_avatar_config import ProductAvatarConfig


def test_seller_can_set_avatar_config_for_owned_product(
    client,
    create_seller,
    create_product,
    auth_header_factory,
    db_session,
):
    seller = create_seller()
    product = create_product(seller_id=seller.id)
    headers = auth_header_factory(seller)

    response = client.post(
        f"/api/v1/seller/products/{product.id}/avatar-config",
        headers=headers,
        json={"avatar_preset_id": 5, "style_params": {"pose": "front"}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["avatar_preset_id"] == 5
    config = db_session.query(ProductAvatarConfig).filter_by(product_id=product.id).one()
    assert config.style_params == {"pose": "front"}


def test_seller_cannot_set_config_for_other_seller_product(
    client,
    create_seller,
    create_product,
    auth_header_factory,
):
    owner = create_seller(email="owner@example.com")
    other = create_seller(email="other@example.com")
    product = create_product(seller_id=owner.id)
    headers = auth_header_factory(other)

    response = client.post(
        f"/api/v1/seller/products/{product.id}/avatar-config",
        headers=headers,
        json={"avatar_preset_id": 1},
    )

    assert response.status_code == 403


def test_get_avatar_config_returns_saved_config(
    client,
    create_seller,
    create_product,
    auth_header_factory,
    db_session,
):
    seller = create_seller()
    product = create_product(seller_id=seller.id)
    db_session.add(
        ProductAvatarConfig(
            product_id=product.id,
            avatar_preset_id=2,
            style_params={"pose": "side"},
        )
    )
    db_session.commit()
    headers = auth_header_factory(seller)

    response = client.get(
        f"/api/v1/seller/products/{product.id}/avatar-config",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["avatar_preset_id"] == 2


def test_get_avatar_config_returns_404_if_not_exists(
    client,
    create_seller,
    create_product,
    auth_header_factory,
):
    seller = create_seller()
    product = create_product(seller_id=seller.id)
    headers = auth_header_factory(seller)

    response = client.get(
        f"/api/v1/seller/products/{product.id}/avatar-config",
        headers=headers,
    )

    assert response.status_code == 404

from decimal import Decimal

import pytest

from app.models.product import ProductStatus
from app.models.user import UserRole
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import ProductService
from tests.conftest import create_product


@pytest.fixture()
def product_service():
    return ProductService(ProductRepository())


def test_list_products_applies_filters_and_pagination(
    product_service,
    db_session,
    create_seller,
):
    seller = create_seller()
    create_product(
        db_session,
        seller_id=seller.id,
        category="tops",
        price=Decimal("20.00"),
    )
    create_product(
        db_session,
        seller_id=seller.id,
        category="tops",
        price=Decimal("50.00"),
    )

    result = product_service.list_products(
        db_session,
        category="tops",
        price_min=Decimal("30"),
        page=1,
        page_size=1,
    )

    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].price >= Decimal("30")


def test_get_product_detail_raises_error_if_not_found_or_deleted(
    product_service,
    db_session,
    create_seller,
):
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id)

    detail = product_service.get_product_detail(db_session, product_id=product.id)
    assert detail.id == product.id

    product.status = ProductStatus.DELETED
    db_session.commit()

    with pytest.raises(Exception):
        product_service.get_product_detail(db_session, product_id=product.id)


def test_create_product_for_seller_sets_correct_seller_id(
    product_service,
    db_session,
    create_seller,
):
    seller = create_seller()
    data = ProductCreate(
        name="Boots",
        description="Leather",
        price=Decimal("120.00"),
        category="footwear",
        gender="unisex",
        stock=5,
    )

    result = product_service.create_product_for_seller(
        db_session,
        seller=seller,
        data=data,
    )

    assert result.seller.id == seller.id


def test_soft_delete_product_changes_status(
    product_service,
    db_session,
    create_seller,
):
    seller = create_seller()
    product = create_product(db_session, seller_id=seller.id)

    product_service.soft_delete_product(
        db_session,
        product_id=product.id,
        seller=seller,
    )

    db_session.refresh(product)
    assert product.status == ProductStatus.DELETED

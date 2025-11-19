from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product, ProductStatus
from app.models.user import User, UserRole
from app.repositories.product_repository import ProductRepository
from app.schemas.product import (
    ProductCreate,
    ProductDetail,
    ProductListResponse,
    ProductUpdate,
)


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def list_products(
        self,
        db: Session,
        *,
        category: Optional[str] = None,
        price_min: Optional[Decimal] = None,
        price_max: Optional[Decimal] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
        gender: Optional[str] = None,
        sort: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ProductListResponse:
        products, total = self.product_repo.list(
            db,
            category=category,
            price_min=price_min,
            price_max=price_max,
            size=size,
            color=color,
            gender=gender,
            sort=sort,
            page=page,
            page_size=page_size,
        )
        items = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "category": product.category,
                "gender": product.gender,
                "main_image_url": product.images[0].url if product.images else None,
                "seller_id": product.seller_id,
            }
            for product in products
        ]
        return ProductListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_product_detail(self, db: Session, *, product_id: int) -> ProductDetail:
        product = self.product_repo.get(db, product_id)
        if not product or product.status == ProductStatus.DELETED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        return ProductDetail.model_validate(product)

    def _ensure_seller_permissions(self, user: User) -> None:
        if user.role not in {UserRole.SELLER, UserRole.ADMIN}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seller permissions required",
            )

    def create_product_for_seller(
        self,
        db: Session,
        *,
        seller: User,
        data: ProductCreate,
    ) -> ProductDetail:
        self._ensure_seller_permissions(seller)
        product = self.product_repo.create(db, seller_id=seller.id, data=data)
        return ProductDetail.model_validate(product)

    def _get_product_or_404(self, db: Session, product_id: int) -> Product:
        product = self.product_repo.get(db, product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        return product

    def _ensure_ownership(self, product: Product, user: User) -> None:
        if user.role != UserRole.ADMIN and product.seller_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this product",
            )

    def update_seller_product(
        self,
        db: Session,
        *,
        product_id: int,
        seller: User,
        data: ProductUpdate,
    ) -> ProductDetail:
        self._ensure_seller_permissions(seller)
        product = self._get_product_or_404(db, product_id)
        self._ensure_ownership(product, seller)
        updated = self.product_repo.update(db, product=product, data=data)
        return ProductDetail.model_validate(updated)

    def soft_delete_product(
        self,
        db: Session,
        *,
        product_id: int,
        seller: User,
    ) -> None:
        self._ensure_seller_permissions(seller)
        product = self._get_product_or_404(db, product_id)
        self._ensure_ownership(product, seller)
        self.product_repo.soft_delete(db, product=product)

from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.models.product import Product, ProductStatus
from app.models.product_avatar_config import ProductAvatarConfig
from app.models.product_image import ProductImage
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository:
    def get(self, db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    def list(
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
    ) -> Tuple[List[Product], int]:
        query = db.query(Product).filter(Product.status == ProductStatus.ACTIVE)

        if category:
            query = query.filter(Product.category == category)
        if gender:
            query = query.filter(Product.gender == gender)
        if price_min is not None:
            query = query.filter(Product.price >= price_min)
        if price_max is not None:
            query = query.filter(Product.price <= price_max)
        if size:
            query = query.filter(Product.size_options.contains([size]))
        if color:
            query = query.filter(Product.color_options.contains([color]))

        if sort == "price_asc":
            query = query.order_by(asc(Product.price))
        elif sort == "price_desc":
            query = query.order_by(desc(Product.price))
        elif sort == "popularity":
            query = query.order_by(desc(Product.id))
        else:
            query = query.order_by(desc(Product.created_at))

        total = query.count()
        items = (
            query.offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def create(self, db: Session, *, seller_id: int, data: ProductCreate) -> Product:
        product = Product(
            seller_id=seller_id,
            name=data.name,
            description=data.description,
            price=data.price,
            category=data.category,
            gender=data.gender,
            size_options=data.size_options,
            color_options=data.color_options,
            variants=data.variants,
            stock=data.stock,
        )
        db.add(product)
        db.flush()
        self._replace_relations(product, data.images, data.avatar_configs)
        db.commit()
        db.refresh(product)
        return product

    def update(self, db: Session, *, product: Product, data: ProductUpdate) -> Product:
        for field, value in data.model_dump(exclude_unset=True).items():
            if field in {"images", "avatar_configs"}:
                continue
            setattr(product, field, value)

        if data.images is not None or data.avatar_configs is not None:
            self._replace_relations(product, data.images, data.avatar_configs)

        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def _replace_relations(
        self,
        product: Product,
        images_data,
        avatar_configs_data,
    ) -> None:
        if images_data is not None:
            product.images = [
                ProductImage(
                    url=image.url,
                    is_avatar_preview=image.is_avatar_preview,
                    sort_order=image.sort_order,
                )
                for image in images_data
            ]
        if avatar_configs_data is not None:
            product.avatar_configs = [
                ProductAvatarConfig(
                    avatar_preset_id=config.avatar_preset_id,
                    style_params=config.style_params,
                )
                for config in avatar_configs_data
            ]

    def soft_delete(self, db: Session, *, product: Product) -> Product:
        product.status = ProductStatus.DELETED
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

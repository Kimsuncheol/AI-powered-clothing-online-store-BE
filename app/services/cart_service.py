from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.product import Product, ProductStatus
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartItemCreate, CartSchema


class CartService:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def get_cart_for_user(self, db: Session, user_id: int) -> CartSchema:
        cart = self.cart_repo.get_or_create_cart(db, user_id)
        db.refresh(cart)
        return CartSchema.model_validate(cart)

    def add_item_to_cart(
        self,
        db: Session,
        user_id: int,
        data: CartItemCreate,
    ) -> CartSchema:
        if data.quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than zero",
            )
        self._get_active_product(db, data.product_id)
        cart = self.cart_repo.get_or_create_cart(db, user_id)

        existing_item = next(
            (
                item
                for item in cart.items
                if item.product_id == data.product_id
                and item.variant_data == data.variant_data
            ),
            None,
        )
        if existing_item:
            new_quantity = existing_item.quantity + data.quantity
            self.cart_repo.update_item_quantity(db, existing_item, new_quantity)
        else:
            self.cart_repo.add_item(db, cart, data)
        db.refresh(cart)
        return CartSchema.model_validate(cart)

    def update_cart_item_quantity(
        self,
        db: Session,
        user_id: int,
        item_id: int,
        quantity: int,
    ) -> CartSchema:
        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity must be greater than zero",
            )
        item = self.cart_repo.get_item_by_id(db, item_id)
        cart = self._ensure_item_belongs_to_user(item, user_id)
        self.cart_repo.update_item_quantity(db, item, quantity)
        db.refresh(cart)
        return CartSchema.model_validate(cart)

    def remove_cart_item(
        self,
        db: Session,
        user_id: int,
        item_id: int,
    ) -> CartSchema:
        item = self.cart_repo.get_item_by_id(db, item_id)
        cart = self._ensure_item_belongs_to_user(item, user_id)
        self.cart_repo.remove_item(db, item)
        db.refresh(cart)
        return CartSchema.model_validate(cart)

    def _ensure_item_belongs_to_user(self, item, user_id: int):
        if item is None or item.cart is None or item.cart.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found",
            )
        return item.cart

    def _get_active_product(self, db: Session, product_id: int) -> Product:
        product = self.product_repo.get(db, product_id)
        if not product or product.status != ProductStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        return product

from typing import Optional

from sqlalchemy.orm import Session

from app.models.cart import Cart, CartItem
from app.schemas.cart import CartItemCreate


class CartRepository:
    def get_or_create_cart(self, db: Session, user_id: int) -> Cart:
        cart = self.get_cart(db, user_id)
        if cart is None:
            cart = Cart(user_id=user_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        return cart

    def get_cart(self, db: Session, user_id: int) -> Optional[Cart]:
        return db.query(Cart).filter(Cart.user_id == user_id).first()

    def add_item(self, db: Session, cart: Cart, data: CartItemCreate) -> CartItem:
        item = CartItem(
            cart_id=cart.id,
            product_id=data.product_id,
            quantity=data.quantity,
            variant_data=data.variant_data,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        db.refresh(cart)
        return item

    def get_item_by_id(self, db: Session, item_id: int) -> Optional[CartItem]:
        return db.query(CartItem).filter(CartItem.id == item_id).first()

    def update_item_quantity(self, db: Session, item: CartItem, quantity: int) -> CartItem:
        item.quantity = quantity
        db.add(item)
        db.commit()
        db.refresh(item)
        if item.cart is not None:
            db.refresh(item.cart)
        return item

    def remove_item(self, db: Session, item: CartItem) -> None:
        cart = item.cart
        db.delete(item)
        db.commit()
        if cart is not None:
            db.refresh(cart)

from fastapi import Depends

from app.core.config import settings
from app.core.paypal_client import PayPalClient
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.paypal_event_repository import PayPalEventRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repo)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo)


def get_product_repository() -> ProductRepository:
    return ProductRepository()


def get_product_service(
    product_repo: ProductRepository = Depends(get_product_repository),
) -> ProductService:
    return ProductService(product_repo)


def get_cart_repository() -> CartRepository:
    return CartRepository()


def get_order_repository() -> OrderRepository:
    return OrderRepository()


def get_payment_repository() -> PaymentRepository:
    return PaymentRepository()


def get_paypal_event_repository() -> PayPalEventRepository:
    return PayPalEventRepository()


def get_paypal_client() -> PayPalClient:
    return PayPalClient(
        client_id=settings.PAYPAL_CLIENT_ID,
        client_secret=settings.PAYPAL_CLIENT_SECRET,
        base_url=settings.PAYPAL_BASE_URL,
    )


def get_cart_service(
    cart_repo: CartRepository = Depends(get_cart_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> CartService:
    return CartService(cart_repo, product_repo)


def get_order_service(
    cart_repo: CartRepository = Depends(get_cart_repository),
    order_repo: OrderRepository = Depends(get_order_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> OrderService:
    return OrderService(cart_repo, order_repo, product_repo)


def get_payment_service(
    payment_repo: PaymentRepository = Depends(get_payment_repository),
    order_repo: OrderRepository = Depends(get_order_repository),
    paypal_client: PayPalClient = Depends(get_paypal_client),
    paypal_event_repo: PayPalEventRepository = Depends(get_paypal_event_repository),
) -> PaymentService:
    return PaymentService(payment_repo, order_repo, paypal_client, paypal_event_repo)

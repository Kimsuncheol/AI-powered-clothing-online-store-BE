from fastapi import Depends

from app.core.config import settings
from app.core.paypal_client import PayPalClient
from app.ai.llm_client import get_llm
from app.ai.stylist_chain import StylistChain
from app.ai.tools.product_search_tool import ProductSearchTool
from app.db.session import SessionLocal
from app.repositories.ai_conversation_repository import AiConversationRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.paypal_event_repository import PayPalEventRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.services.ai_stylist_service import AiStylistService
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.services.user_service import UserService


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


def get_ai_conversation_repository() -> AiConversationRepository:
    return AiConversationRepository()


def get_product_search_tool_dependency(
    product_service: ProductService = Depends(get_product_service),
) -> ProductSearchTool:
    return ProductSearchTool(product_service, SessionLocal)


def get_stylist_chain(
    product_search_tool: ProductSearchTool = Depends(get_product_search_tool_dependency),
):
    llm = get_llm()
    return StylistChain(llm=llm, product_search_tool=product_search_tool.to_langchain_tool())


def get_ai_stylist_service(
    ai_conv_repo: AiConversationRepository = Depends(get_ai_conversation_repository),
    product_service: ProductService = Depends(get_product_service),
    stylist_chain: StylistChain = Depends(get_stylist_chain),
) -> AiStylistService:
    return AiStylistService(ai_conv_repo, product_service, stylist_chain)


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

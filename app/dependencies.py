from fastapi import Depends

from app.core.config import settings
from app.core.paypal_client import PayPalClient
from app.ai.llm_client import get_llm
from app.ai.stylist_chain import StylistChain
from app.ai.seller_chain import SellerChain
from app.ai.avatar_chain import AvatarChain
from app.ai.tools.product_search_tool import ProductSearchTool
from app.ai.tools.seller_tools import SellerTools
from app.db.session import SessionLocal
from app.core.image_client import ImageClient
from app.repositories.ai_conversation_repository import AiConversationRepository
from app.repositories.ai_avatar_request_repository import AiAvatarRequestRepository
from app.repositories.avatar_preset_repository import AvatarPresetRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.paypal_event_repository import PayPalEventRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.repositories.search_repository import SearchRepository
from app.services.ai_stylist_service import AiStylistService
from app.services.ai_seller_service import AiSellerService
from app.services.avatar_preset_service import AvatarPresetService
from app.services.ai_avatar_service import AiAvatarService
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.services.user_service import UserService
from app.services.search_service import SearchService


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


def get_avatar_preset_repository() -> AvatarPresetRepository:
    return AvatarPresetRepository()


def get_ai_avatar_request_repository() -> AiAvatarRequestRepository:
    return AiAvatarRequestRepository()


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


def get_seller_tools(
    product_service: ProductService = Depends(get_product_service),
) -> SellerTools:
    return SellerTools(product_service, SessionLocal)


def get_seller_chain(
    seller_tools: SellerTools = Depends(get_seller_tools),
) -> SellerChain:
    llm = get_llm()
    return SellerChain(llm=llm, tools=seller_tools.to_langchain_tools())


def get_ai_seller_service(
    ai_conv_repo: AiConversationRepository = Depends(get_ai_conversation_repository),
    product_service: ProductService = Depends(get_product_service),
    seller_chain: SellerChain = Depends(get_seller_chain),
) -> AiSellerService:
    return AiSellerService(ai_conv_repo, product_service, seller_chain)


def get_image_client() -> ImageClient:
    return ImageClient(api_key="stub-key", base_url="https://image.api")


def get_avatar_chain(
    image_client: ImageClient = Depends(get_image_client),
):
    llm = get_llm()
    return AvatarChain(llm=llm, image_client=image_client)


def get_avatar_preset_service(
    preset_repo: AvatarPresetRepository = Depends(get_avatar_preset_repository),
) -> AvatarPresetService:
    return AvatarPresetService(preset_repo)


def get_ai_avatar_service(
    ai_avatar_repo: AiAvatarRequestRepository = Depends(get_ai_avatar_request_repository),
    preset_repo: AvatarPresetRepository = Depends(get_avatar_preset_repository),
    product_service: ProductService = Depends(get_product_service),
    avatar_chain: AvatarChain = Depends(get_avatar_chain),
) -> AiAvatarService:
    return AiAvatarService(ai_avatar_repo, preset_repo, product_service, avatar_chain)


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


from app.services.admin_service import AdminService


def get_admin_service(
    user_repo: UserRepository = Depends(get_user_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
    order_repo: OrderRepository = Depends(get_order_repository),
) -> AdminService:
    return AdminService(user_repo, product_repo, order_repo)


def get_search_repository() -> SearchRepository:
    return SearchRepository()


def get_search_service(
    search_repo: SearchRepository = Depends(get_search_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> SearchService:
    return SearchService(search_repo, product_repo)

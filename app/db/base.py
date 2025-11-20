"""
Import all SQLAlchemy models here so that Alembic or any metadata consumers
are aware of them. This file should only import models and expose Base.
"""
from app.db.base_class import Base

# Import models to ensure they are registered with SQLAlchemy metadata
from app.models.user import User  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.product_image import ProductImage  # noqa: F401
from app.models.product_avatar_config import ProductAvatarConfig  # noqa: F401
from app.models.avatar_preset import AvatarPreset  # noqa: F401
from app.models.ai_avatar_request import AiAvatarRequest  # noqa: F401
from app.models.cart import Cart, CartItem  # noqa: F401
from app.models.order import Order, OrderItem  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.paypal_event import PayPalEvent  # noqa: F401
from app.models.ai_conversation import AiConversation  # noqa: F401
from app.models.search_keyword import SearchKeyword  # noqa: F401

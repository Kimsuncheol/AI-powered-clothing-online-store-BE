import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.ai.stylist_chain import StylistChain
from app.models.ai_conversation import AiConversation, AiConversationType
from app.repositories.ai_conversation_repository import AiConversationRepository
from app.schemas.ai import (
    ProductRecommendationSummary,
    StylistChatResponse,
)
from app.services.product_service import ProductService


class AiStylistService:
    def __init__(
        self,
        ai_conv_repo: AiConversationRepository,
        product_service: ProductService,
        stylist_chain: StylistChain,
    ):
        self.ai_conv_repo = ai_conv_repo
        self.product_service = product_service
        self.stylist_chain = stylist_chain

    def handle_chat(
        self,
        db: Session,
        *,
        user_id: int,
        user_message: str,
        product_id: Optional[int],
        conversation_id: Optional[str],
    ) -> StylistChatResponse:
        conversation, messages = self._load_or_create_conversation(
            db,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        timestamp = datetime.utcnow().isoformat()
        messages.append(
            {
                "role": "user",
                "content": user_message,
                "timestamp": timestamp,
            }
        )

        product_context = self._get_product_context(db, product_id)
        reply_text, recommendations_raw = self.stylist_chain.run(
            messages=messages,
            user_message=user_message,
            product_context=product_context,
        )

        messages.append(
            {
                "role": "assistant",
                "content": reply_text,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self.ai_conv_repo.update_messages(
            db,
            conversation=conversation,
            messages=messages,
        )

        recommendations = self._map_recommendations(recommendations_raw)
        return StylistChatResponse(
            replyText=reply_text,
            conversationId=conversation.conversation_id,
            recommendations=recommendations,
        )

    def _load_or_create_conversation(
        self,
        db: Session,
        *,
        user_id: int,
        conversation_id: Optional[str],
    ) -> Tuple[AiConversation, List[Dict[str, Any]]]:
        conv_type = AiConversationType.STYLIST
        conversation = None
        messages: List[Dict[str, Any]] = []

        if conversation_id:
            conversation = self.ai_conv_repo.get_by_conversation_id(
                db,
                conversation_id=conversation_id,
                conv_type=conv_type,
                user_id=user_id,
            )
            if conversation and conversation.messages:
                messages = list(conversation.messages)

        if not conversation:
            new_id = conversation_id or str(uuid.uuid4())
            conversation = self.ai_conv_repo.create(
                db,
                user_id=user_id,
                conv_type=conv_type,
                conversation_id=new_id,
                messages=messages,
            )
            messages = list(conversation.messages or [])

        return conversation, messages

    def _get_product_context(
        self,
        db: Session,
        product_id: Optional[int],
    ) -> Optional[Dict[str, Any]]:
        if product_id is None:
            return None

        product = self.product_service.get_product_for_context(
            db,
            product_id=product_id,
        )
        if not product:
            return None

        return {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": str(product.price),
        }

    def _map_recommendations(
        self,
        recommendations_raw: List[Dict[str, Any]],
    ) -> List[ProductRecommendationSummary]:
        mapped: List[ProductRecommendationSummary] = []
        for item in recommendations_raw or []:
            mapped.append(
                ProductRecommendationSummary(
                    id=item["id"],
                    title=item["title"],
                    price=Decimal(str(item["price"])),
                    image=item.get("image"),
                )
            )
        return mapped

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.ai.seller_chain import SellerChain
from app.models.ai_conversation import AiConversationType
from app.repositories.ai_conversation_repository import AiConversationRepository
from app.schemas.ai import (
    GenerateDescriptionRequest,
    GenerateDescriptionResponse,
    SellerChatResponse,
)
from app.services.product_service import ProductService


class AiSellerService:
    def __init__(
        self,
        ai_conv_repo: AiConversationRepository,
        product_service: ProductService,
        seller_chain: SellerChain,
    ):
        self.ai_conv_repo = ai_conv_repo
        self.product_service = product_service
        self.seller_chain = seller_chain

    def handle_chat(
        self,
        db: Session,
        *,
        user_id: int,
        user_message: str,
        product_id: Optional[int],
        conversation_id: Optional[str],
    ) -> SellerChatResponse:
        conv_type = AiConversationType.SELLER
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
                messages=[],
            )
            messages = []

        messages.append(
            {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        product_context = None
        if product_id is not None:
            product = self.product_service.get_product_for_context(
                db,
                product_id=product_id,
            )
            if product:
                product_context = {
                    "id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "price": str(product.price),
                }

        chain_output = self.seller_chain.chat(
            messages=messages,
            user_message=user_message,
            product_context=product_context,
        )

        reply_text = chain_output.get("replyText", "")
        messages.append(
            {
                "role": "assistant",
                "content": reply_text,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        self.ai_conv_repo.update_messages(db, conversation=conversation, messages=messages)

        return SellerChatResponse(
            replyText=reply_text,
            conversationId=conversation.conversation_id,
            generatedTitle=chain_output.get("generatedTitle"),
            generatedDescription=chain_output.get("generatedDescription"),
            generatedTags=chain_output.get("generatedTags"),
        )

    def generate_description(
        self,
        *,
        basic_fields: GenerateDescriptionRequest,
    ) -> GenerateDescriptionResponse:
        return self.seller_chain.generate_description(basic_fields.dict())

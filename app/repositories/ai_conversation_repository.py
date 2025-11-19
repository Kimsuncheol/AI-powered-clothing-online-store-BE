from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.ai_conversation import AiConversation, AiConversationType


class AiConversationRepository:
    def get_by_conversation_id(
        self,
        db: Session,
        *,
        conversation_id: str,
        conv_type: AiConversationType,
        user_id: int,
    ) -> Optional[AiConversation]:
        return (
            db.query(AiConversation)
            .filter(
                AiConversation.conversation_id == conversation_id,
                AiConversation.type == conv_type,
                AiConversation.user_id == user_id,
            )
            .first()
        )

    def create(
        self,
        db: Session,
        *,
        user_id: int,
        conv_type: AiConversationType,
        conversation_id: str,
        messages: List[Dict[str, Any]],
    ) -> AiConversation:
        conversation = AiConversation(
            user_id=user_id,
            type=conv_type,
            conversation_id=conversation_id,
            messages=messages,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    def update_messages(
        self,
        db: Session,
        *,
        conversation: AiConversation,
        messages: List[Dict[str, Any]],
    ) -> AiConversation:
        conversation.messages = messages
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.dependencies import get_ai_stylist_service
from app.models.user import User
from app.schemas.ai import StylistChatRequest, StylistChatResponse
from app.services.ai_stylist_service import AiStylistService
from app.db.session import get_db

router = APIRouter(prefix="/ai/stylist", tags=["ai-stylist"])


@router.post("/chat", response_model=StylistChatResponse)
def stylist_chat(
    body: StylistChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_stylist_service: AiStylistService = Depends(get_ai_stylist_service),
) -> StylistChatResponse:
    """
    Buyer-facing AI Stylist chat endpoint wired to the LangChain powered service.
    """
    return ai_stylist_service.handle_chat(
        db,
        user_id=current_user.id,
        user_message=body.userMessage,
        product_id=body.productId,
        conversation_id=body.conversationId,
    )

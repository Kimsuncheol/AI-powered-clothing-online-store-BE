from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.dependencies import get_ai_seller_service
from app.models.user import User
from app.schemas.ai import (
    GenerateDescriptionRequest,
    GenerateDescriptionResponse,
    SellerChatRequest,
    SellerChatResponse,
)
from app.services.ai_seller_service import AiSellerService

router = APIRouter(prefix="/ai/seller", tags=["ai-seller"])


@router.post("/chat", response_model=SellerChatResponse)
def seller_chat(
    body: SellerChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_seller_service: AiSellerService = Depends(get_ai_seller_service),
) -> SellerChatResponse:
    """
    Seller-facing AI assistant leveraging seller-specific LangChain tools.
    """
    return ai_seller_service.handle_chat(
        db,
        user_id=current_user.id,
        user_message=body.userMessage,
        product_id=body.productId,
        conversation_id=body.conversationId,
    )


@router.post("/generate-description", response_model=GenerateDescriptionResponse)
def generate_description(
    body: GenerateDescriptionRequest,
    current_user: User = Depends(get_current_user),
    ai_seller_service: AiSellerService = Depends(get_ai_seller_service),
) -> GenerateDescriptionResponse:
    """
    Used by FE 'Generate with AI' button in seller product form.
    """
    return ai_seller_service.generate_description(basic_fields=body)

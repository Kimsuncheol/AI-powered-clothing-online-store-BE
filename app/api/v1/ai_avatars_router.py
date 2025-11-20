from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.dependencies import get_ai_avatar_service
from app.models.user import User
from app.schemas.avatar import AvatarRenderRequest, AvatarRenderResponse
from app.services.ai_avatar_service import AiAvatarService

router = APIRouter(prefix="/ai/avatars", tags=["ai-avatars"])


@router.post("/render", response_model=AvatarRenderResponse)
def render_avatar(
    body: AvatarRenderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    ai_avatar_service: AiAvatarService = Depends(get_ai_avatar_service),
) -> AvatarRenderResponse:
    return ai_avatar_service.render_avatars(
        db,
        user_id=current_user.id,
        product_id=body.productId,
        avatar_preset_id=body.avatarPresetId,
        style_params=body.styleParams,
        image_count=body.imageCount,
    )

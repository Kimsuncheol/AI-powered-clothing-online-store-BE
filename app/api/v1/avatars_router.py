from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_avatar_preset_service
from app.schemas.avatar import AvatarPresetListResponse
from app.services.avatar_preset_service import AvatarPresetService

router = APIRouter(prefix="/avatars", tags=["avatars"])


@router.get("/presets", response_model=AvatarPresetListResponse)
def list_avatar_presets(
    db: Session = Depends(get_db),
    avatar_preset_service: AvatarPresetService = Depends(get_avatar_preset_service),
) -> AvatarPresetListResponse:
    presets = avatar_preset_service.list_active_presets(db)
    return AvatarPresetListResponse(items=presets)

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.ai_avatar_request import AiAvatarRequest, AiAvatarRequestStatus


class AiAvatarRequestRepository:
    def create(
        self,
        db: Session,
        *,
        request_id: str,
        user_id: int,
        product_id: Optional[int],
        avatar_preset_id: int,
        style_params: Optional[Dict[str, Any]],
        image_count: int,
    ) -> AiAvatarRequest:
        ai_request = AiAvatarRequest(
            request_id=request_id,
            user_id=user_id,
            product_id=product_id,
            avatar_preset_id=avatar_preset_id,
            style_params=style_params,
            image_count=image_count,
            status=AiAvatarRequestStatus.PENDING,
        )
        db.add(ai_request)
        db.commit()
        db.refresh(ai_request)
        return ai_request

    def update_result(
        self,
        db: Session,
        *,
        ai_request: AiAvatarRequest,
        status: AiAvatarRequestStatus,
        image_urls: List[str],
    ) -> AiAvatarRequest:
        ai_request.status = status
        ai_request.image_urls = image_urls
        db.add(ai_request)
        db.commit()
        db.refresh(ai_request)
        return ai_request

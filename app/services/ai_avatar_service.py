import uuid
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.avatar_chain import AvatarChain
from app.models.ai_avatar_request import AiAvatarRequestStatus
from app.models.avatar_preset import AvatarPresetStatus
from app.models.product_image import ProductImage
from app.repositories.ai_avatar_request_repository import AiAvatarRequestRepository
from app.repositories.avatar_preset_repository import AvatarPresetRepository
from app.schemas.avatar import AvatarRenderResponse
from app.services.product_service import ProductService


class AiAvatarService:
    def __init__(
        self,
        ai_avatar_repo: AiAvatarRequestRepository,
        preset_repo: AvatarPresetRepository,
        product_service: ProductService,
        avatar_chain: AvatarChain,
    ):
        self.ai_avatar_repo = ai_avatar_repo
        self.preset_repo = preset_repo
        self.product_service = product_service
        self.avatar_chain = avatar_chain

    def render_avatars(
        self,
        db: Session,
        *,
        user_id: int,
        product_id: Optional[int],
        avatar_preset_id: int,
        style_params: Optional[Dict[str, Any]],
        image_count: int,
    ) -> AvatarRenderResponse:
        preset = self.preset_repo.get_by_id(db, avatar_preset_id)
        if not preset or preset.status != AvatarPresetStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or inactive avatar preset.",
            )

        product = None
        if product_id is not None:
            product = self.product_service.get_product_for_context(
                db,
                product_id=product_id,
            )

        request_id = str(uuid.uuid4())
        ai_request = self.ai_avatar_repo.create(
            db,
            request_id=request_id,
            user_id=user_id,
            product_id=product_id,
            avatar_preset_id=avatar_preset_id,
            style_params=style_params,
            image_count=image_count,
        )

        preset_params = preset.parameters or {}
        image_urls = self.avatar_chain.generate_avatar_images(
            product=product,
            preset_params=preset_params,
            style_params=style_params,
            image_count=image_count,
        )

        ai_request = self.ai_avatar_repo.update_result(
            db,
            ai_request=ai_request,
            status=AiAvatarRequestStatus.COMPLETED,
            image_urls=image_urls,
        )

        if product and image_urls:
            db.add_all(
                [
                    ProductImage(
                        product_id=product.id,
                        url=url,
                        is_avatar_preview=True,
                        sort_order=idx,
                    )
                    for idx, url in enumerate(image_urls)
                ]
            )
            db.commit()

        return AvatarRenderResponse(
            requestId=ai_request.request_id,
            imageUrls=image_urls,
        )

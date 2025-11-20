from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models.ai_avatar_request import AiAvatarRequest
from app.models.avatar_preset import AvatarPresetStatus
from app.models.product_image import ProductImage
from app.repositories.ai_avatar_request_repository import AiAvatarRequestRepository
from app.repositories.avatar_preset_repository import AvatarPresetRepository
from app.schemas.avatar import AvatarPresetCreate, AvatarPresetParameters
from app.services.ai_avatar_service import AiAvatarService


def _create_preset(db_session, repo: AvatarPresetRepository):
    return repo.create(
        db_session,
        AvatarPresetCreate(
            name="Preset",
            parameters=AvatarPresetParameters(body_type="slim"),
            status=AvatarPresetStatus.ACTIVE,
        ),
    )


def test_render_avatars_creates_ai_request_and_returns_urls(
    db_session,
    create_seller,
):
    repo = AvatarPresetRepository()
    ai_repo = AiAvatarRequestRepository()
    preset = _create_preset(db_session, repo)
    product_service = MagicMock()
    product_service.get_product_for_context.return_value = None
    avatar_chain = MagicMock()
    avatar_chain.generate_avatar_images.return_value = ["url1", "url2"]
    service = AiAvatarService(ai_repo, repo, product_service, avatar_chain)
    user = create_seller()

    response = service.render_avatars(
        db_session,
        user_id=user.id,
        product_id=None,
        avatar_preset_id=preset.id,
        style_params={"pose": "front"},
        image_count=2,
    )

    assert response.imageUrls == ["url1", "url2"]
    req = db_session.query(AiAvatarRequest).one()
    assert req.image_urls == ["url1", "url2"]


def test_render_avatars_validates_preset_is_active(
    db_session,
    create_seller,
):
    repo = AvatarPresetRepository()
    ai_repo = AiAvatarRequestRepository()
    preset = repo.create(
        db_session,
        AvatarPresetCreate(
            name="Inactive",
            parameters=AvatarPresetParameters(),
            status=AvatarPresetStatus.INACTIVE,
        ),
    )
    service = AiAvatarService(ai_repo, repo, MagicMock(), MagicMock())
    user = create_seller()

    with pytest.raises(HTTPException):
        service.render_avatars(
            db_session,
            user_id=user.id,
            product_id=None,
            avatar_preset_id=preset.id,
            style_params=None,
            image_count=1,
        )


def test_render_avatars_with_product_saves_product_images(
    db_session,
    create_seller,
    create_product,
):
    repo = AvatarPresetRepository()
    ai_repo = AiAvatarRequestRepository()
    preset = _create_preset(db_session, repo)
    seller = create_seller()
    product = create_product(seller_id=seller.id)
    product_service = MagicMock()
    product_service.get_product_for_context.return_value = product
    avatar_chain = MagicMock()
    avatar_chain.generate_avatar_images.return_value = ["img1", "img2"]
    service = AiAvatarService(ai_repo, repo, product_service, avatar_chain)

    response = service.render_avatars(
        db_session,
        user_id=seller.id,
        product_id=product.id,
        avatar_preset_id=preset.id,
        style_params=None,
        image_count=2,
    )

    assert response.imageUrls == ["img1", "img2"]
    images = (
        db_session.query(ProductImage)
        .filter(ProductImage.product_id == product.id, ProductImage.is_avatar_preview.is_(True))
        .all()
    )
    assert len(images) == 2
    product_service.get_product_for_context.assert_called_once()


def test_render_avatars_without_product_does_not_create_product_images(
    db_session,
    create_seller,
):
    repo = AvatarPresetRepository()
    ai_repo = AiAvatarRequestRepository()
    preset = _create_preset(db_session, repo)
    product_service = MagicMock()
    product_service.get_product_for_context.return_value = None
    avatar_chain = MagicMock()
    avatar_chain.generate_avatar_images.return_value = ["only"]
    service = AiAvatarService(ai_repo, repo, product_service, avatar_chain)
    user = create_seller()

    service.render_avatars(
        db_session,
        user_id=user.id,
        product_id=None,
        avatar_preset_id=preset.id,
        style_params=None,
        image_count=1,
    )

    assert db_session.query(ProductImage).count() == 0

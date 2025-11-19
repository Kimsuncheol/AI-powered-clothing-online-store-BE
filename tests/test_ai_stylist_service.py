from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.models.ai_conversation import AiConversationType
from app.repositories.ai_conversation_repository import AiConversationRepository
from app.services.ai_stylist_service import AiStylistService


@pytest.fixture()
def ai_conv_repo() -> AiConversationRepository:
    return AiConversationRepository()


def test_handle_chat_creates_new_conversation_when_none_given(
    db_session,
    create_buyer,
    ai_conv_repo,
):
    user = create_buyer()
    stylist_chain = MagicMock()
    stylist_chain.run.return_value = ("Hi buyer!", [])
    service = AiStylistService(ai_conv_repo, MagicMock(), stylist_chain)

    response = service.handle_chat(
        db_session,
        user_id=user.id,
        user_message="Need outfit ideas",
        product_id=None,
        conversation_id=None,
    )

    assert response.conversationId
    conversation = ai_conv_repo.get_by_conversation_id(
        db_session,
        conversation_id=response.conversationId,
        conv_type=AiConversationType.STYLIST,
        user_id=user.id,
    )
    assert conversation is not None
    assert len(conversation.messages) == 2  # user + assistant


def test_handle_chat_appends_to_existing_conversation(
    db_session,
    create_buyer,
    ai_conv_repo,
):
    user = create_buyer()
    existing = ai_conv_repo.create(
        db_session,
        user_id=user.id,
        conv_type=AiConversationType.STYLIST,
        conversation_id="conv-123",
        messages=[
            {"role": "user", "content": "Hi", "timestamp": "t1"},
            {"role": "assistant", "content": "Hello", "timestamp": "t2"},
        ],
    )
    stylist_chain = MagicMock()
    stylist_chain.run.return_value = ("Second response", [])
    product_service = MagicMock()
    service = AiStylistService(ai_conv_repo, product_service, stylist_chain)
    original_len = len(existing.messages)

    response = service.handle_chat(
        db_session,
        user_id=user.id,
        user_message="Another question",
        product_id=None,
        conversation_id=existing.conversation_id,
    )

    assert response.conversationId == existing.conversation_id
    updated = ai_conv_repo.get_by_conversation_id(
        db_session,
        conversation_id=existing.conversation_id,
        conv_type=AiConversationType.STYLIST,
        user_id=user.id,
    )
    assert len(updated.messages) == original_len + 2


def test_handle_chat_includes_product_context_when_product_id_present(
    db_session,
    create_buyer,
    ai_conv_repo,
):
    user = create_buyer()
    product = SimpleNamespace(
        id=99,
        name="Silk Dress",
        category="DRESSES",
        price=Decimal("129.00"),
    )
    product_service = MagicMock()
    product_service.get_product_for_context.return_value = product
    stylist_chain = MagicMock()
    stylist_chain.run.return_value = ("Styled!", [])
    service = AiStylistService(ai_conv_repo, product_service, stylist_chain)

    service.handle_chat(
        db_session,
        user_id=user.id,
        user_message="Recommend me something elegant",
        product_id=product.id,
        conversation_id=None,
    )

    args = stylist_chain.run.call_args.kwargs
    assert args["product_context"] == {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "price": str(product.price),
    }


def test_handle_chat_maps_recommendations_to_schema(
    db_session,
    create_buyer,
    ai_conv_repo,
):
    user = create_buyer()
    stylist_chain = MagicMock()
    stylist_chain.run.return_value = (
        "Here are some looks",
        [
            {"id": 1, "title": "Cozy Knit", "price": "59.99", "image": "img1"},
            {"id": 2, "title": "Denim Jacket", "price": Decimal("129.00"), "image": None},
        ],
    )
    service = AiStylistService(ai_conv_repo, MagicMock(), stylist_chain)

    response = service.handle_chat(
        db_session,
        user_id=user.id,
        user_message="Need fall outfits",
        product_id=None,
        conversation_id=None,
    )

    assert len(response.recommendations) == 2
    assert response.recommendations[0].title == "Cozy Knit"
    assert response.recommendations[0].price == Decimal("59.99")
    assert response.recommendations[1].price == Decimal("129.00")

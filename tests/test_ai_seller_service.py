from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.models.ai_conversation import AiConversationType
from app.repositories.ai_conversation_repository import AiConversationRepository
from app.schemas.ai import GenerateDescriptionRequest, GenerateDescriptionResponse
from app.services.ai_seller_service import AiSellerService


@pytest.fixture()
def ai_conv_repo() -> AiConversationRepository:
    return AiConversationRepository()


def test_handle_chat_creates_new_seller_conversation_if_not_exists(
    db_session,
    create_seller,
    ai_conv_repo,
):
    user = create_seller()
    product_service = MagicMock()
    seller_chain = MagicMock()
    seller_chain.chat.return_value = {"replyText": "Hello seller!"}
    service = AiSellerService(ai_conv_repo, product_service, seller_chain)

    response = service.handle_chat(
        db_session,
        user_id=user.id,
        user_message="How do I price this product?",
        product_id=None,
        conversation_id=None,
    )

    assert response.replyText == "Hello seller!"
    assert response.conversationId
    conversation = ai_conv_repo.get_by_conversation_id(
        db_session,
        conversation_id=response.conversationId,
        conv_type=AiConversationType.SELLER,
        user_id=user.id,
    )
    assert conversation is not None
    assert len(conversation.messages) == 2  # user + assistant


def test_handle_chat_appends_to_existing_conversation(
    db_session,
    create_seller,
    ai_conv_repo,
):
    user = create_seller()
    existing = ai_conv_repo.create(
        db_session,
        user_id=user.id,
        conv_type=AiConversationType.SELLER,
        conversation_id="seller-conv-1",
        messages=[{"role": "user", "content": "Hi", "timestamp": "t1"}],
    )
    product_service = MagicMock()
    seller_chain = MagicMock()
    seller_chain.chat.return_value = {"replyText": "Continuing the chat"}
    service = AiSellerService(ai_conv_repo, product_service, seller_chain)

    response = service.handle_chat(
        db_session,
        user_id=user.id,
        user_message="New question",
        product_id=None,
        conversation_id=existing.conversation_id,
    )

    assert response.conversationId == existing.conversation_id
    updated = ai_conv_repo.get_by_conversation_id(
        db_session,
        conversation_id=existing.conversation_id,
        conv_type=AiConversationType.SELLER,
        user_id=user.id,
    )
    assert len(updated.messages) == len(existing.messages) + 2


def test_handle_chat_passes_product_context_when_product_id_set(
    db_session,
    create_seller,
    ai_conv_repo,
):
    user = create_seller()
    product = SimpleNamespace(
        id=7,
        name="Premium Hoodie",
        category="HOODIES",
        price=Decimal("79.00"),
    )
    product_service = MagicMock()
    product_service.get_product_for_context.return_value = product
    seller_chain = MagicMock()
    seller_chain.chat.return_value = {"replyText": "Here you go"}
    service = AiSellerService(ai_conv_repo, product_service, seller_chain)

    service.handle_chat(
        db_session,
        user_id=user.id,
        user_message="Generate a title",
        product_id=product.id,
        conversation_id=None,
    )

    seller_chain.chat.assert_called_once()
    kwargs = seller_chain.chat.call_args.kwargs
    assert kwargs["product_context"] == {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "price": str(product.price),
    }


def test_handle_chat_returns_structured_data_from_chain_output(
    db_session,
    create_seller,
    ai_conv_repo,
):
    user = create_seller()
    product_service = MagicMock()
    seller_chain = MagicMock()
    seller_chain.chat.return_value = {
        "replyText": "Draft ready",
        "generatedTitle": "AI Title",
        "generatedDescription": "AI Description",
        "generatedTags": ["tag1", "tag2"],
    }
    service = AiSellerService(ai_conv_repo, product_service, seller_chain)

    response = service.handle_chat(
        db_session,
        user_id=user.id,
        user_message="Assist me",
        product_id=None,
        conversation_id=None,
    )

    assert response.generatedTitle == "AI Title"
    assert response.generatedDescription == "AI Description"
    assert response.generatedTags == ["tag1", "tag2"]


def test_generate_description_delegates_to_seller_chain(ai_conv_repo):
    product_service = MagicMock()
    seller_chain = MagicMock()
    result = GenerateDescriptionResponse(
        title="T",
        description="D",
        tags=["x"],
    )
    seller_chain.generate_description.return_value = result
    service = AiSellerService(ai_conv_repo, product_service, seller_chain)

    request = GenerateDescriptionRequest(name="Cozy Sweater")
    response = service.generate_description(basic_fields=request)

    assert response is result
    seller_chain.generate_description.assert_called_once()
    args, _ = seller_chain.generate_description.call_args
    assert args[0] == request.dict()

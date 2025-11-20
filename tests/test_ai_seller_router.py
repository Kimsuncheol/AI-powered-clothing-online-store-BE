from app.dependencies import get_ai_seller_service
from app.schemas.ai import (
    GenerateDescriptionResponse,
    SellerChatResponse,
)
from main import app


def test_seller_chat_requires_auth(client):
    response = client.post(
        "/api/v1/ai/seller/chat",
        json={"userMessage": "Help me"},
    )
    assert response.status_code == 401


def test_seller_chat_returns_reply_and_conversation_id(
    client,
    create_seller,
    auth_header_factory,
):
    user = create_seller()
    headers = auth_header_factory(user)

    class DummyService:
        def handle_chat(self, *args, **kwargs):
            return SellerChatResponse(
                replyText="Hello seller",
                conversationId="seller-conv",
                generatedTitle="Generated Title",
                generatedDescription="Generated Description",
                generatedTags=["tag"],
            )

    app.dependency_overrides[get_ai_seller_service] = lambda: DummyService()
    try:
        response = client.post(
            "/api/v1/ai/seller/chat",
            headers=headers,
            json={"userMessage": "Need title"},
        )
    finally:
        del app.dependency_overrides[get_ai_seller_service]

    assert response.status_code == 200
    payload = response.json()
    assert payload["replyText"] == "Hello seller"
    assert payload["conversationId"] == "seller-conv"
    assert payload["generatedTitle"] == "Generated Title"


def test_generate_description_requires_auth(client):
    response = client.post(
        "/api/v1/ai/seller/generate-description",
        json={},
    )
    assert response.status_code == 401


def test_generate_description_returns_title_description_tags(
    client,
    create_seller,
    auth_header_factory,
):
    user = create_seller()
    headers = auth_header_factory(user)

    class DummyService:
        def generate_description(self, *args, **kwargs):
            return GenerateDescriptionResponse(
                title="AI Title",
                description="AI Description",
                tags=["tag1", "tag2"],
            )

    app.dependency_overrides[get_ai_seller_service] = lambda: DummyService()
    try:
        response = client.post(
            "/api/v1/ai/seller/generate-description",
            headers=headers,
            json={"name": "Cozy Tee"},
        )
    finally:
        del app.dependency_overrides[get_ai_seller_service]

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "AI Title"
    assert payload["description"] == "AI Description"
    assert payload["tags"] == ["tag1", "tag2"]

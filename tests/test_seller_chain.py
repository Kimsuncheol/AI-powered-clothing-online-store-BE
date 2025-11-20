from types import SimpleNamespace

from app.ai.seller_chain import SellerChain


class DummyLLM:
    def __init__(self):
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return SimpleNamespace(content="LLM reply")


def test_chat_returns_reply_text_and_tracks_product_context():
    llm = DummyLLM()
    chain = SellerChain(llm=llm, tools=[])

    output = chain.chat(
        messages=[{"role": "user", "content": "Hi"}],
        user_message="Need pricing advice",
        product_context={"id": 1, "name": "Cozy Tee"},
    )

    assert output["replyText"] == "LLM reply"
    assert llm.calls, "LLM should be invoked"
    assert any(
        "Product context" in getattr(msg, "content", "")
        for msg in llm.calls[0]
    )


def test_generate_description_returns_strings_and_tags():
    chain = SellerChain(llm=DummyLLM(), tools=[])

    response = chain.generate_description(
        {
            "name": "Premium Hoodie",
            "category": "Hoodies",
            "gender": "Unisex",
            "price": "79.00",
            "style_keywords": ["cozy", "streetwear"],
        }
    )

    assert isinstance(response.title, str) and response.title
    assert isinstance(response.description, str) and response.description
    assert isinstance(response.tags, list)
    assert response.tags

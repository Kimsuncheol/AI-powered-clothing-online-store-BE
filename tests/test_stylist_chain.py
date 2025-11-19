from types import SimpleNamespace

from app.ai.stylist_chain import StylistChain


class DummyLLM:
    def __init__(self):
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return SimpleNamespace(content="LLM reply")


class RecordingTool:
    def __init__(self, response=None):
        self.queries = []
        self.response = response or [
            {"id": 1, "title": "Party Dress", "price": "99.00", "image": None}
        ]

    def run(self, query: str):
        self.queries.append(query)
        return self.response


def test_run_returns_llm_reply_and_recommendations_with_product_context():
    llm = DummyLLM()
    tool = RecordingTool()
    chain = StylistChain(llm=llm, product_search_tool=tool)

    reply, recommendations = chain.run(
        messages=[{"role": "user", "content": "Hi"}],
        user_message="Can you recommend a party dress?",
        product_context={"id": 1, "name": "Slip Dress"},
    )

    assert reply == "LLM reply"
    assert recommendations == tool.response
    assert tool.queries == ["Can you recommend a party dress?"]
    assert any("Product context" in msg.content for msg in llm.calls[0])


def test_run_skips_tool_when_no_recommendation_intent():
    llm = DummyLLM()
    tool = RecordingTool()
    chain = StylistChain(llm=llm, product_search_tool=tool)

    _, recommendations = chain.run(
        messages=[],
        user_message="Hello stylist",
        product_context=None,
    )

    assert recommendations == []
    assert tool.queries == []


def test_run_swallows_tool_errors():
    class BrokenTool:
        def run(self, query: str):
            raise RuntimeError("boom")

    llm = DummyLLM()
    chain = StylistChain(llm=llm, product_search_tool=BrokenTool())

    _, recommendations = chain.run(
        messages=[],
        user_message="Need outfit ideas and recommendations",
        product_context=None,
    )

    assert recommendations == []
    assert len(llm.calls) == 1

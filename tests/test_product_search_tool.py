from types import SimpleNamespace
from unittest.mock import MagicMock

from app.ai.tools.product_search_tool import ProductSearchTool


class DummySession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_search_tool_returns_formatted_products():
    product_service = MagicMock()
    product_service.search_products.return_value = [
        SimpleNamespace(
            id=1,
            name="Evening Dress",
            price="199.00",
            images=[SimpleNamespace(url="image-1")],
        )
    ]

    session = DummySession()
    tool = ProductSearchTool(product_service, lambda: session)

    results = tool._search("evening")

    assert results == [
        {
            "id": 1,
            "title": "Evening Dress",
            "price": "199.00",
            "image": "image-1",
        }
    ]
    product_service.search_products.assert_called_once()
    assert session.closed


def test_to_langchain_tool_exposes_callable_func():
    product_service = MagicMock()
    product_service.search_products.return_value = []
    session = DummySession()
    tool = ProductSearchTool(product_service, lambda: session)

    lc_tool = tool.to_langchain_tool()
    lc_tool.func("casual look")

    product_service.search_products.assert_called_once()
    args, kwargs = product_service.search_products.call_args
    assert args[0] is session
    assert kwargs["query"] == "casual look"
    assert kwargs["limit"] == tool.default_limit
    assert session.closed

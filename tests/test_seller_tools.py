from types import SimpleNamespace
from unittest.mock import MagicMock

from app.ai.tools.seller_tools import SellerTools


class DummySession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def _call_tool(tool, *args, **kwargs):
    if hasattr(tool, "func"):
        return tool.func(*args, **kwargs)
    return tool(*args, **kwargs)


def test_get_product_detail_returns_expected_dict():
    product = SimpleNamespace(
        id=10,
        name="Casual Tee",
        category="TOPS",
        gender="WOMEN",
        price="29.00",
        stock=50,
    )
    product_service = MagicMock()
    product_service.get_product_for_context.return_value = product
    session = DummySession()
    tools = SellerTools(product_service, lambda: session)

    detail = tools._get_product_detail(product.id)

    assert detail == {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "gender": product.gender,
        "price": str(product.price),
        "stock": product.stock,
    }
    assert session.closed


def test_get_market_stats_returns_stub():
    product_service = MagicMock()
    tools = SellerTools(product_service, lambda: DummySession())

    stats = tools._get_market_stats("DRESSES")

    assert stats["category"] == "DRESSES"
    assert "avg_price" in stats and "notes" in stats


def test_to_langchain_tools_returns_tools_with_expected_output():
    product = SimpleNamespace(
        id=12,
        name="Denim Jacket",
        category="JACKETS",
        gender="UNISEX",
        price="129.00",
        stock=5,
    )
    product_service = MagicMock()
    product_service.get_product_for_context.return_value = product
    session = DummySession()
    tools = SellerTools(product_service, lambda: session)

    lc_tools = tools.to_langchain_tools()
    names = {tool.name for tool in lc_tools}
    assert names == {"get_product_detail", "get_market_stats"}

    product_tool = next(tool for tool in lc_tools if tool.name == "get_product_detail")
    stats_tool = next(tool for tool in lc_tools if tool.name == "get_market_stats")

    product_detail = _call_tool(product_tool, str(product.id))
    stats_detail = _call_tool(stats_tool, category="TOPS")

    assert product_detail["name"] == product.name
    assert stats_detail["category"] == "TOPS"
    assert session.closed

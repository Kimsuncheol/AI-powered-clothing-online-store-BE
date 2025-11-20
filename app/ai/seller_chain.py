from typing import Any, Dict, List, Optional, TypedDict

from app.schemas.ai import GenerateDescriptionResponse

try:
    from langchain.schema import AIMessage, HumanMessage, SystemMessage
except ImportError:  # pragma: no cover - fallback lightweight message classes

    class _BaseMessage:
        def __init__(self, content: str):
            self.content = content

    class SystemMessage(_BaseMessage):
        pass

    class HumanMessage(_BaseMessage):
        pass

    class AIMessage(_BaseMessage):
        pass

try:
    from langchain.tools import Tool
except ImportError:  # pragma: no cover - keep runtime working without langchain
    from app.ai.tools.seller_tools import Tool  # type: ignore


SELLER_SYSTEM_PROMPT = """
You are an AI e-commerce coach helping clothing sellers optimize their listings.
- Help write high-converting product titles and descriptions.
- Generate SEO-friendly tags.
- Give pricing suggestions with clear reasoning.
- Use tools like get_product_detail and get_market_stats when they are relevant.
- Return structured data when you generate titles, descriptions, and tags.
""".strip()


class SellerChainOutput(TypedDict, total=False):
    replyText: str
    generatedTitle: str
    generatedDescription: str
    generatedTags: List[str]


class SellerChain:
    def __init__(self, llm: Any, tools: Optional[List[Tool]] = None):
        self.llm = llm
        self.tools = tools or []

    def chat(
        self,
        *,
        messages: List[Dict[str, Any]],
        user_message: str,
        product_context: Optional[Dict[str, Any]] = None,
    ) -> SellerChainOutput:
        """
        Generic chat entry point.
        Should return:
          - replyText (required)
          - optionally generatedTitle, generatedDescription, generatedTags
        """
        lc_messages: List[Any] = [SystemMessage(content=SELLER_SYSTEM_PROMPT)]
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")
            if role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        if product_context:
            lc_messages.append(
                HumanMessage(
                    content=f"Product context shared by seller: {product_context}",
                )
            )

        lc_messages.append(HumanMessage(content=user_message))
        llm_response = self.llm.invoke(lc_messages)
        reply_text = getattr(llm_response, "content", str(llm_response))
        return SellerChainOutput(replyText=reply_text)

    def generate_description(self, basic_fields: Dict[str, Any]) -> GenerateDescriptionResponse:
        """
        Specialised method for 'Generate Description' endpoint.
        Use llm to generate title, description, tags from minimal product info.
        """
        name = basic_fields.get("name") or basic_fields.get("category") or "Product"
        category = basic_fields.get("category") or ""
        gender = basic_fields.get("gender") or ""
        price = basic_fields.get("price")
        style_keywords = basic_fields.get("style_keywords") or []
        target_audience = basic_fields.get("target_audience") or "customers"

        title_parts = [part for part in [gender, category, name] if part]
        title = " ".join(title_parts) or "AI-Optimized Product Title"

        description_sections = [
            f"Introducing the {name}, crafted for {target_audience}.",
        ]
        if style_keywords:
            keywords = ", ".join(style_keywords)
            description_sections.append(f"Style highlights: {keywords}.")
        if price:
            description_sections.append(f"Suggested price point: {price}.")
        if basic_fields.get("existing_description"):
            description_sections.append(
                "We refined your original description for clarity and conversions."
            )
        description = " ".join(description_sections)

        tags = style_keywords or []
        if category:
            tags.append(category.lower())
        if gender:
            tags.append(gender.lower())

        if not tags:
            tags = ["fashion", "ai-generated"]

        return GenerateDescriptionResponse(
            title=title,
            description=description,
            tags=list(dict.fromkeys(tags)),  # preserve order, remove duplicates
        )

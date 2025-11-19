from typing import Any, Dict, List, Optional, Tuple

from app.ai.tools.product_search_tool import Tool

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


SYSTEM_PROMPT = """
You are an AI fashion stylist for an online clothing store.
- Speak in a friendly, concise, and helpful tone.
- Ask clarifying questions if needed (occasion, weather, style).
- Use the `search_products` tool when the user needs concrete product suggestions.
- Always respond with suggestions that exist in the catalog when using product search results.
""".strip()


class StylistChain:
    def __init__(self, llm: Any, product_search_tool: Optional[Tool] = None):
        self.llm = llm
        self.product_search_tool = product_search_tool

    def run(
        self,
        *,
        messages: List[Dict[str, Any]],
        user_message: str,
        product_context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        lc_messages: List[Any] = [SystemMessage(content=SYSTEM_PROMPT)]
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
                    content=f"Product context shared by user: {product_context}",
                )
            )

        recommendations = self._maybe_get_recommendations(user_message)
        if recommendations:
            lc_messages.append(
                HumanMessage(
                    content=f"Product recommendations considered: {recommendations}",
                )
            )

        llm_response = self.llm.invoke(lc_messages)
        reply_text = getattr(llm_response, "content", str(llm_response))
        return reply_text, recommendations

    def _maybe_get_recommendations(self, user_message: str) -> List[Dict[str, Any]]:
        if not self.product_search_tool:
            return []
        intent_keywords = ["recommend", "suggest", "idea", "outfit", "dress", "look"]
        lowered = user_message.lower()
        if not any(keyword in lowered for keyword in intent_keywords):
            return []

        try:
            return self._invoke_search_tool(user_message)
        except Exception:
            # Tool failures should not break the stylist flow; fall back silently.
            return []

    def _invoke_search_tool(self, query: str) -> List[Dict[str, Any]]:
        if hasattr(self.product_search_tool, "run"):
            return self.product_search_tool.run(query)
        if hasattr(self.product_search_tool, "func"):
            return self.product_search_tool.func(query)
        if callable(self.product_search_tool):
            return self.product_search_tool(query)
        raise RuntimeError("Configured product search tool is not callable")

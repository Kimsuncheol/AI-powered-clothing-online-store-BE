from dataclasses import dataclass
from typing import Any, Iterable, Optional


@dataclass
class _LLMResult:
    content: str


class FallbackChatModel:
    """
    Lightweight stand-in for ChatOpenAI used in test environments where
    LangChain/OpenAI clients are unavailable. It simply echoes a canned
    response to keep the request pipeline functional.
    """

    def __init__(self, default_response: str = "Thanks for chatting with our stylist!"):
        self.default_response = default_response

    def invoke(self, messages: Iterable[Any]) -> _LLMResult:
        # Echo the last human message to keep local dev flows deterministic.
        last_content: Optional[str] = None
        for msg in messages:
            content = getattr(msg, "content", None)
            if content:
                last_content = content
        response = last_content or self.default_response
        return _LLMResult(content=response)


def get_llm(model_name: str = "gpt-4o-mini", temperature: float = 0.3) -> Any:
    """
    Return a LangChain ChatOpenAI client if available, otherwise fall back to a
    simple deterministic stub so the application and tests remain runnable
    without the heavy dependency.
    """
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        return FallbackChatModel()

    return ChatOpenAI(model=model_name, temperature=temperature)

from typing import Literal

from pydantic import BaseModel

Role = Literal["user", "model"]


class ChatMessage(BaseModel):
    """A single turn in a multi-turn LLM conversation, provider-agnostic.

    ``role`` follows Gemini's vocabulary ("user" / "model"); OpenAI-compatible
    providers map "model" to "assistant" at the transport layer.
    """

    role: Role
    content: str

    @classmethod
    def user(cls, content: str) -> "ChatMessage":
        return cls(role="user", content=content)

    @classmethod
    def model(cls, content: str) -> "ChatMessage":
        return cls(role="model", content=content)

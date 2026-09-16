from __future__ import annotations
from typing import AsyncIterator, TypedDict, Literal

class ChatMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str

class BaseChatProvider:
    name: str

    def __init__(self, model: str | None = None) -> None:
        self.model = model

    async def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        raise NotImplementedError

    async def complete(
        self,
        messages: list[ChatMessage],
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs
    ) -> str:
        tokens = []
        async for token in self.stream(messages):
            tokens.append(token)
        return "".join(tokens)

class BaseEmbeddingProvider:
    name: str
    dim: int

    def __init__(self, model: str | None = None, dim: int | None = None) -> None:
        self.model = model
        self.dim = dim or 768

    async def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

from __future__ import annotations
import json
from typing import AsyncIterator
import httpx
from app.config import settings
from app.ai.providers.base import BaseChatProvider, BaseEmbeddingProvider, ChatMessage

OPENAI_BASE = "https://api.openai.com/v1"

class OpenAIChatProvider(BaseChatProvider):
    name = "openai"

    def __init__(self, model: str | None = None, api_key: str | None = None, base_url: str | None = None) -> None:
        self.model = model or "gpt-4o"
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = (base_url or OPENAI_BASE).rstrip("/")

    async def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        payload = {"model": self.model, "messages": messages, "stream": True}
        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[len("data:") :].strip()
                    if data == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    choices = obj.get("choices", [])
                    if choices:
                        token = choices[0].get("delta", {}).get("content")
                        if token:
                            yield token

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    name = "openai"

    def __init__(self, model: str | None = None, dim: int | None = None, api_key: str | None = None) -> None:
        super().__init__(model or "text-embedding-3-small", dim or settings.EMBEDDING_DIM)
        self.api_key = api_key or settings.OPENAI_API_KEY

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        payload = {"model": self.model, "input": texts, "dimensions": self.dim}
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{OPENAI_BASE}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]

from __future__ import annotations
import json
from typing import AsyncIterator, List
import httpx
from app.config import settings
from app.ai.providers.base import BaseChatProvider, BaseEmbeddingProvider, ChatMessage

class OllamaChatProvider(BaseChatProvider):
    name = "ollama"

    def __init__(self, model: str | None = None, base_url: str | None = None) -> None:
        self.model = model or settings.DEFAULT_MODEL
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")

    async def ping(self) -> dict:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            models = [m.get("name") for m in data.get("models", [])]
            return {"status": "online", "models": models}

    async def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": True},
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    token = obj.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if obj.get("done"):
                        break

class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    name = "ollama"

    def __init__(self, model: str | None = None, dim: int | None = None, base_url: str | None = None) -> None:
        super().__init__(model or settings.EMBEDDING_MODEL, dim or settings.EMBEDDING_DIM)
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")

    async def embed(self, texts: list[str]) -> list[list[float]]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": texts},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["embeddings"]

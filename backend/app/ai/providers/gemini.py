from __future__ import annotations
import json
from typing import AsyncIterator
import httpx
from app.config import settings
from app.ai.providers.base import BaseChatProvider, ChatMessage

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/openai"

class GeminiChatProvider(BaseChatProvider):
    name = "gemini"

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model = model or "gemini-1.5-pro"
        self.api_key = api_key or settings.GEMINI_API_KEY

    async def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        payload = {"model": self.model, "messages": messages, "stream": True}
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{GEMINI_BASE}/chat/completions",
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

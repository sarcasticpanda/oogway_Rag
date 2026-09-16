from __future__ import annotations
import json
from typing import AsyncIterator
import httpx
from app.config import settings
from app.ai.providers.base import BaseChatProvider, ChatMessage

OPENROUTER_BASE = "https://openrouter.ai/api/v1"

class OpenRouterChatProvider(BaseChatProvider):
    name = "openrouter"

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        # Default to a free model on OpenRouter if none specified
        self.model = model or "meta-llama/llama-3.1-8b-instruct:free"
        self.api_key = api_key or settings.OPENROUTER_API_KEY

    async def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is not configured.")

        payload = {"model": self.model, "messages": messages, "stream": True}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:5173", # Recommended by OpenRouter
            "X-Title": "Lenny Growth Assistant"      # Recommended by OpenRouter
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{OPENROUTER_BASE}/chat/completions",
                headers=headers,
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

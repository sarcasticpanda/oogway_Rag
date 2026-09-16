from __future__ import annotations
import json
from typing import AsyncIterator
import httpx
from app.config import settings
from app.ai.providers.base import BaseChatProvider, ChatMessage

ANTHROPIC_BASE = "https://api.anthropic.com/v1"

class AnthropicChatProvider(BaseChatProvider):
    name = "anthropic"

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model = model or "claude-3-5-sonnet-20241022"
        self.api_key = api_key or settings.ANTHROPIC_API_KEY

    async def stream(self, messages: list[ChatMessage]) -> AsyncIterator[str]:
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        convo = [m for m in messages if m["role"] != "system"]

        payload = {
            "model": self.model,
            "system": system,
            "messages": convo,
            "max_tokens": 4096,
            "stream": True,
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream(
                "POST", f"{ANTHROPIC_BASE}/messages", headers=headers, json=payload
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[len("data:") :].strip()
                    try:
                        obj = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    if obj.get("type") == "content_block_delta":
                        token = obj.get("delta", {}).get("text")
                        if token:
                            yield token
                    elif obj.get("type") == "message_stop":
                        break

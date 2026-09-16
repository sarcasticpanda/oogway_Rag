import httpx
from typing import List, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/models", tags=["models"])

class ModelSwitchRequest(BaseModel):
    provider: str
    model: str

@router.get("")
async def get_models_info():
    """
    Returns the system's provider and model availability:
    - Checks live Ollama daemon connectivity and lists locally installed models.
    - Reports configured cloud models (Anthropic Claude, OpenAI GPT-4o).
    - Indicates the active default provider and model.
    """
    ollama_status = "offline"
    ollama_models: List[str] = []

    # Dynamic probe to local Ollama
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                ollama_status = "online"
                data = resp.json()
                ollama_models = [m.get("name") for m in data.get("models", [])]
    except Exception:
        ollama_status = "offline"

    available_providers = ["ollama"]
    cloud_providers = []

    if settings.ANTHROPIC_API_KEY:
        available_providers.append("anthropic")
        cloud_providers.append({
            "name": "anthropic",
            "displayName": "Anthropic Claude",
            "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
            "configured": True
        })
    else:
        cloud_providers.append({
            "name": "anthropic",
            "displayName": "Anthropic Claude",
            "models": ["claude-3-5-sonnet-20241022"],
            "configured": False,
            "note": "ANTHROPIC_API_KEY not configured in .env"
        })

    if settings.OPENAI_API_KEY:
        available_providers.append("openai")
        cloud_providers.append({
            "name": "openai",
            "displayName": "OpenAI",
            "models": ["gpt-4o", "gpt-4o-mini"],
            "configured": True
        })
    else:
        cloud_providers.append({
            "name": "openai",
            "displayName": "OpenAI",
            "models": ["gpt-4o", "gpt-4o-mini"],
            "configured": False,
            "note": "OPENAI_API_KEY not configured in .env"
        })

    return {
        "active_provider": settings.AI_PROVIDER,
        "active_model": settings.DEFAULT_MODEL,
        "available_providers": available_providers,
        "ollama": {
            "status": ollama_status,
            "endpoint": settings.OLLAMA_BASE_URL,
            "models": ollama_models if ollama_models else ["llama3.1", "mistral", "nomic-embed-text"]
        },
        "cloud_providers": cloud_providers
    }

@router.post("/switch")
async def switch_model(req: ModelSwitchRequest):
    """Dynamically switch system default provider and model."""
    settings.AI_PROVIDER = req.provider.lower()
    settings.DEFAULT_MODEL = req.model
    return {
        "status": "success",
        "active_provider": settings.AI_PROVIDER,
        "active_model": settings.DEFAULT_MODEL
    }

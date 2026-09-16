from app.config import settings
from app.ai.providers.base import BaseChatProvider, BaseEmbeddingProvider
from app.ai.providers.ollama import OllamaChatProvider, OllamaEmbeddingProvider
from app.ai.providers.anthropic import AnthropicChatProvider
from app.ai.providers.openai import OpenAIChatProvider, OpenAIEmbeddingProvider
from app.ai.providers.groq import GroqChatProvider
from app.ai.providers.gemini import GeminiChatProvider
from app.ai.providers.openrouter import OpenRouterChatProvider
class AIProviderFactory:
    @staticmethod
    def get_chat_provider(
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None
    ) -> BaseChatProvider:
        selected_provider = (provider or settings.AI_PROVIDER).lower()

        if selected_provider == "ollama":
            return OllamaChatProvider(model=model or settings.DEFAULT_MODEL, base_url=base_url)
        elif selected_provider == "anthropic":
            return AnthropicChatProvider(model=model or "claude-3-5-sonnet-20241022", api_key=api_key)
        elif selected_provider == "openai":
            return OpenAIChatProvider(model=model or "gpt-4o", api_key=api_key, base_url=base_url)
        elif selected_provider == "groq":
            return GroqChatProvider(model=model or "openai/gpt-oss-20b", api_key=api_key)
        elif selected_provider == "gemini":
            return GeminiChatProvider(model=model or "gemini-1.5-pro", api_key=api_key)
        elif selected_provider == "openrouter":
            return OpenRouterChatProvider(model=model or "meta-llama/llama-3.1-8b-instruct:free", api_key=api_key)
        elif selected_provider == "custom":
            if not base_url:
                raise ValueError("A base URL is required for a custom provider.")
            return OpenAIChatProvider(model=model or "default", api_key=api_key, base_url=base_url)
        else:
            # Fallback to Ollama
            return OllamaChatProvider(model=model or settings.DEFAULT_MODEL)

    @staticmethod
    def get_embedding_provider(
        provider: str | None = None,
        model: str | None = None
    ) -> BaseEmbeddingProvider:
        selected_provider = (provider or settings.EMBEDDING_PROVIDER).lower()

        if selected_provider == "openai":
            return OpenAIEmbeddingProvider(
                model=model or "text-embedding-3-small",
                dim=settings.EMBEDDING_DIM
            )
        else:
            return OllamaEmbeddingProvider(
                model=model or settings.EMBEDDING_MODEL,
                dim=settings.EMBEDDING_DIM
            )

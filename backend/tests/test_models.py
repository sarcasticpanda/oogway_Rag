import pytest
from app.ai.factory import AIProviderFactory
from app.ai.providers.ollama import OllamaChatProvider, OllamaEmbeddingProvider
from app.ai.providers.anthropic import AnthropicChatProvider
from app.ai.providers.openai import OpenAIChatProvider, OpenAIEmbeddingProvider

def test_model_factory_provider_selection():
    """Verify that factory resolves requested provider classes accurately."""
    # Ollama Chat
    ollama_provider = AIProviderFactory.get_chat_provider("ollama", "llama3.1")
    assert isinstance(ollama_provider, OllamaChatProvider)
    assert ollama_provider.model == "llama3.1"

    # Anthropic Chat
    anthropic_provider = AIProviderFactory.get_chat_provider("anthropic", "claude-3-5-sonnet-20241022")
    assert isinstance(anthropic_provider, AnthropicChatProvider)

    # OpenAI Chat
    openai_provider = AIProviderFactory.get_chat_provider("openai", "gpt-4o")
    assert isinstance(openai_provider, OpenAIChatProvider)

    # Fallback for unknown provider defaults safely to Ollama
    fallback_provider = AIProviderFactory.get_chat_provider("unknown_provider")
    assert isinstance(fallback_provider, OllamaChatProvider)

def test_embedding_factory_selection():
    """Verify that embedding provider factory returns appropriate embedding handler."""
    ollama_emb = AIProviderFactory.get_embedding_provider("ollama", "nomic-embed-text")
    assert isinstance(ollama_emb, OllamaEmbeddingProvider)

    openai_emb = AIProviderFactory.get_embedding_provider("openai", "text-embedding-3-small")
    assert isinstance(openai_emb, OpenAIEmbeddingProvider)

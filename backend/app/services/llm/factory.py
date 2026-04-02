from app.services.llm.base import BaseLLMProvider
from app.services.llm.groq_provider import GroqProvider
from app.core.config import settings


_providers = {
    "groq":      GroqProvider,
    # "openai":    OpenAIProvider,      ← will add in next steps
    # "anthropic": AnthropicProvider,   ← will add in next steps
    # "gemini":    GeminiProvider,      ← will add in next steps
}


def get_llm_provider(provider: str = None) -> BaseLLMProvider:
    name = provider or settings.DEFAULT_LLM_PROVIDER
    if name not in _providers:
        raise ValueError(f"Unknown LLM provider: '{name}'. Available: {list(_providers.keys())}")
    return _providers[name]()
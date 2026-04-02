from langchain_community.embeddings import JinaEmbeddings
from app.core.config import settings


def get_embedding_model(provider: str = "jina"):
    """
    Returns LangChain embedding model based on provider.
    Default: Jina (free + high quality)
    """

    if provider == "jina":
        return JinaEmbeddings(
            jina_api_key=settings.JINA_API_KEY,
            model_name=settings.EMBEDDING_MODEL    # ← from config, not hardcoded
        )

    elif provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )

    elif provider == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            google_api_key=settings.GEMINI_API_KEY,
            model="models/embedding-001"
        )

    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")


def get_default_embedding_model():
    """Auto-picks best available embedding model from config"""
    if settings.JINA_API_KEY:
        return get_embedding_model("jina")
    elif settings.OPENAI_API_KEY:
        return get_embedding_model("openai")
    elif settings.GEMINI_API_KEY:
        return get_embedding_model("gemini")
    else:
        raise ValueError("No embedding API key found. Set JINA_API_KEY in .env")
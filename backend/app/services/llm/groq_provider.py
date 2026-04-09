from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.services.llm.base import BaseLLMProvider
from app.core.config import settings
from typing import AsyncGenerator


class GroqProvider(BaseLLMProvider):

    def _resolve_model(self, model: str = None) -> str:
        available_models = settings.GROQ_MODELS
        selected_model = model or settings.DEFAULT_GROQ_MODEL
        if selected_model not in available_models:
            return settings.DEFAULT_GROQ_MODEL if settings.DEFAULT_GROQ_MODEL in available_models else available_models[0]
        return selected_model

    def _build_messages(self, messages: list[dict]):
        result = []
        for m in messages:
            if m["role"] == "system":
                result.append(SystemMessage(content=m["content"]))
            elif m["role"] == "user":
                result.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                result.append(AIMessage(content=m["content"]))
        return result

    async def chat(
        self,
        messages: list[dict],
        model: str = None,
        **kwargs
    ) -> str:
        model = self._resolve_model(model)
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model=model)
        response = await llm.ainvoke(self._build_messages(messages))
        return response.content

    async def stream_chat(
        self,
        messages: list[dict],
        model: str = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        model = self._resolve_model(model)
        llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=model,
            streaming=True
        )
        async for chunk in llm.astream(self._build_messages(messages)):
            if chunk.content:
                yield chunk.content

    def get_available_models(self) -> list[str]:
        return settings.GROQ_MODELS
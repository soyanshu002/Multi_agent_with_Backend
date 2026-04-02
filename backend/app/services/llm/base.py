from abc import ABC, abstractmethod
from typing import AsyncGenerator


class BaseLLMProvider(ABC):

    @abstractmethod
    async def chat(self, messages: list[dict], model: str, **kwargs) -> str:
        """Single response"""
        pass

    @abstractmethod
    async def stream_chat(self, messages: list[dict], model: str, **kwargs) -> AsyncGenerator[str, None]:
        """Streaming response"""
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Return list of supported models"""
        pass
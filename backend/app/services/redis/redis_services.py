import json
from typing import Optional
from redis.asyncio import Redis
from app.core.config import settings


class RedisService:

    def __init__(self):
        self.client: Optional[Redis] = None

    async def connect(self):
        if not settings.REDIS_URL:
            self.client = None
            return
        self.client = Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        if self.client:
            await self.client.aclose()

    # ── Conversation History ───────────────────────
    async def get_history(self, conversation_id: str) -> list[dict]:
        if not self.client:
            return []
        data = await self.client.get(f"chat:{conversation_id}")
        return json.loads(data) if data else []

    async def save_history(self, conversation_id: str, messages: list[dict], ttl: int = 86400):
        """Save chat history. TTL default = 24 hours"""
        if not self.client:
            return
        await self.client.setex(
            f"chat:{conversation_id}",
            ttl,
            json.dumps(messages)
        )

    async def append_message(self, conversation_id: str, message: dict, ttl: int = 86400):
        """Append a single message to existing history"""
        history = await self.get_history(conversation_id)
        history.append(message)
        await self.save_history(conversation_id, history, ttl)

    async def clear_history(self, conversation_id: str):
        if not self.client:
            return
        await self.client.delete(f"chat:{conversation_id}")

    # ── Generic Cache ──────────────────────────────
    async def set(self, key: str, value: str, ttl: int = 3600):
        if self.client:
            await self.client.setex(key, ttl, value)

    async def get(self, key: str) -> Optional[str]:
        if not self.client:
            return None
        return await self.client.get(key)

    async def delete(self, key: str):
        if self.client:
            await self.client.delete(key)

    async def ping(self) -> bool:
        try:
            if not self.client:
                return False
            return await self.client.ping()
        except Exception:
            return False


# ── Singleton ──────────────────────────────────────
redis_service = RedisService()
import redis.asyncio as redis
from src.shared.config import settings
from typing import Optional
import json


class RedisClient:
    _instance: Optional['RedisClient'] = None
    _client: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        """Conecta ao Redis"""
        if self._client is None:
            self._client = await redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                encoding="utf-8",
                decode_responses=True,
            )

    async def disconnect(self):
        """Desconecta do Redis"""
        if self._client:
            await self._client.close()
            self._client = None

    async def get(self, key: str) -> Optional[str]:
        """Obtém valor do cache"""
        if not self._client:
            await self.connect()
        return await self._client.get(key)

    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """Define valor no cache"""
        if not self._client:
            await self.connect()
        await self._client.set(key, value, ex=expire)

    async def delete(self, key: str):
        """Remove valor do cache"""
        if not self._client:
            await self.connect()
        await self._client.delete(key)

    async def get_json(self, key: str) -> Optional[dict]:
        """Obtém JSON do cache"""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(self, key: str, value: dict, expire: Optional[int] = None):
        """Define JSON no cache"""
        await self.set(key, json.dumps(value), expire=expire)


redis_client = RedisClient()


import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")


class RedisClient:
    _instance = None

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = await redis.from_url(REDIS_URL, decode_responses=True)
        return cls._instance

    @classmethod
    async def set_with_expiry(cls, key, value, ttl_seconds=3600):
        redis_instance = await cls.get_instance()
        await redis_instance.setex(key, ttl_seconds, value)

    @classmethod
    async def get(cls, key):
        redis_instance = await cls.get_instance()
        return await redis_instance.get(key)

    @classmethod
    async def close(cls):
        if cls._instance:
            await cls._instance.close()
            cls._instance = None

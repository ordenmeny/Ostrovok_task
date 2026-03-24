from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from blog_app.services.post_cache import build_redis_client


async def get_redis() -> AsyncGenerator[Redis, None]:
    redis = build_redis_client()
    try:
        yield redis
    finally:
        await redis.close()
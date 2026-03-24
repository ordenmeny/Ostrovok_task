import json
import os

from redis.asyncio import Redis

from blog_app.api.schemas import PostRead


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
POST_CACHE_TTL = int(os.getenv("POST_CACHE_TTL", "300"))


def build_redis_client() -> Redis:
    return Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=REDIS_DB,
        decode_responses=True,
    )


def get_post_cache_key(post_id: int) -> str:
    return f"post:{post_id}"


async def get_cached_post(redis: Redis, post_id: int) -> PostRead | None:
    raw = await redis.get(get_post_cache_key(post_id))
    if raw is None:
        return None

    data = json.loads(raw)
    return PostRead.model_validate(data)


async def set_cached_post(redis: Redis, post: PostRead) -> None:
    await redis.set(
        get_post_cache_key(post.id),
        post.model_dump_json(),
        ex=POST_CACHE_TTL,
    )


async def invalidate_post_cache(redis: Redis, post_id: int) -> None:
    await redis.delete(get_post_cache_key(post_id))
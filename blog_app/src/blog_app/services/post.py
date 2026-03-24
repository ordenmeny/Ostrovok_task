from fastapi import HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from blog_app.api.crud import (
    create_post as create_post_db,
    delete_post as delete_post_db,
    get_post_by_id as get_post_by_id_db,
    get_posts as get_posts_db,
    update_post as update_post_db,
)
from blog_app.api.schemas import PostCreate, PostRead, PostUpdate
from blog_app.services.post_cache import (
    get_cached_post,
    invalidate_post_cache,
    set_cached_post,
)


async def create_post(
    session: AsyncSession,
    data: PostCreate,
) -> PostRead:
    post = await create_post_db(session, data)
    return PostRead.model_validate(post)


async def get_posts(
    session: AsyncSession,
) -> list[PostRead]:
    posts = await get_posts_db(session)
    return [PostRead.model_validate(post) for post in posts]


async def get_post_by_id(
    session: AsyncSession,
    redis: Redis,
    post_id: int,
) -> PostRead:
    cached_post = await get_cached_post(redis, post_id)
    if cached_post is not None:
        return cached_post

    post = await get_post_by_id_db(session, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    post_read = PostRead.model_validate(post)
    await set_cached_post(redis, post_read)
    return post_read


async def update_post(
    session: AsyncSession,
    redis: Redis,
    post_id: int,
    data: PostUpdate,
) -> PostRead:
    post = await get_post_by_id_db(session, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    updated_post = await update_post_db(session, post, data)
    await invalidate_post_cache(redis, post_id)

    return PostRead.model_validate(updated_post)


async def delete_post(
    session: AsyncSession,
    redis: Redis,
    post_id: int,
) -> None:
    post = await get_post_by_id_db(session, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    await delete_post_db(session, post)
    await invalidate_post_cache(redis, post_id)
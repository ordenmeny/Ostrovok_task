from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from redis.asyncio import Redis

from blog_app.api.dependencies import get_redis
from blog_app.db.dependencies import SessionDep
from blog_app.api.schemas import PostCreate, PostRead, PostUpdate
from blog_app.services.post import (
    create_post,
    delete_post,
    get_post_by_id,
    get_posts,
    update_post,
)

router = APIRouter(prefix="/posts", tags=["posts"])

RedisDep = Annotated[Redis, Depends(get_redis)]


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post_endpoint(
    data: PostCreate,
    session: SessionDep,
) -> PostRead:
    return await create_post(session, data)


@router.get("", response_model=list[PostRead])
async def get_posts_endpoint(
    session: SessionDep,
) -> list[PostRead]:
    return await get_posts(session)


@router.get("/{post_id}", response_model=PostRead)
async def get_post_by_id_endpoint(
    post_id: int,
    session: SessionDep,
    redis: RedisDep,
) -> PostRead:
    return await get_post_by_id(session, redis, post_id)


@router.patch("/{post_id}", response_model=PostRead)
async def update_post_endpoint(
    post_id: int,
    data: PostUpdate,
    session: SessionDep,
    redis: RedisDep,
) -> PostRead:
    return await update_post(session, redis, post_id, data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_endpoint(
    post_id: int,
    session: SessionDep,
    redis: RedisDep,
) -> Response:
    await delete_post(session, redis, post_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
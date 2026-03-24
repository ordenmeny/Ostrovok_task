from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from blog_app.api.models import Post
from blog_app.api.schemas import PostCreate, PostUpdate


async def create_post(
    session: AsyncSession,
    data: PostCreate,
) -> Post:
    post = Post(
        title=data.title,
        content=data.content,
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


async def get_post_by_id(
    session: AsyncSession,
    post_id: int,
) -> Post | None:
    stmt = select(Post).where(Post.id == post_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_posts(
    session: AsyncSession,
) -> list[Post]:
    stmt = select(Post).order_by(Post.id.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_post(
    session: AsyncSession,
    post: Post,
    data: PostUpdate,
) -> Post:
    if data.title is not None:
        post.title = data.title

    if data.content is not None:
        post.content = data.content

    await session.commit()
    await session.refresh(post)
    return post


async def delete_post(
    session: AsyncSession,
    post: Post,
) -> None:
    await session.delete(post)
    await session.commit()
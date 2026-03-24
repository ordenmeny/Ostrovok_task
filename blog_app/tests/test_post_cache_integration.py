import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from httpx import ASGITransport, AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from blog_app.api.dependencies import get_redis
from blog_app.api.models import Post
from blog_app.db.base import Base
from blog_app.db import helper
from blog_app.main import app


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DB_URL, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


@pytest_asyncio.fixture
async def redis_client():
    redis = FakeRedis(decode_responses=True)
    try:
        yield redis
    finally:
        await redis.flushall()
        await redis.aclose()


@pytest_asyncio.fixture
async def client(session_factory, redis_client):
    old_session_factory = helper.sessionmanager.session_factory
    helper.sessionmanager.session_factory = session_factory

    async def override_get_redis():
        yield redis_client

    app.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as ac:
        yield ac

    helper.sessionmanager.session_factory = old_session_factory
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_post_cache_flow(client: AsyncClient, session_factory, redis_client):
    create_response = await client.post(
        "/posts",
        json={
            "title": "First title",
            "content": "First content",
        },
    )
    assert create_response.status_code == 201

    created_post = create_response.json()
    post_id = created_post["id"]
    cache_key = f"post:{post_id}"

    assert await redis_client.get(cache_key) is None

    first_get_response = await client.get(f"/posts/{post_id}")
    assert first_get_response.status_code == 200
    assert first_get_response.json()["title"] == "First title"
    assert first_get_response.json()["content"] == "First content"

    cached_raw = await redis_client.get(cache_key)
    assert cached_raw is not None

    async with session_factory() as session:
        await session.execute(
            update(Post)
            .where(Post.id == post_id)
            .values(
                title="Changed directly in DB",
                content="Changed directly in DB",
            )
        )
        await session.commit()

    second_get_response = await client.get(f"/posts/{post_id}")
    assert second_get_response.status_code == 200

    second_post = second_get_response.json()
    assert second_post["title"] == "First title"
    assert second_post["content"] == "First content"

    patch_response = await client.patch(
        f"/posts/{post_id}",
        json={
            "title": "Updated title",
            "content": "Updated content",
        },
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["title"] == "Updated title"
    assert patch_response.json()["content"] == "Updated content"

    assert await redis_client.get(cache_key) is None

    third_get_response = await client.get(f"/posts/{post_id}")
    assert third_get_response.status_code == 200

    third_post = third_get_response.json()
    assert third_post["title"] == "Updated title"
    assert third_post["content"] == "Updated content"

    assert await redis_client.get(cache_key) is not None

    delete_response = await client.delete(f"/posts/{post_id}")
    assert delete_response.status_code == 204

    assert await redis_client.get(cache_key) is None

    get_after_delete_response = await client.get(f"/posts/{post_id}")
    assert get_after_delete_response.status_code == 404
    assert get_after_delete_response.json() == {"detail": "Post not found"}
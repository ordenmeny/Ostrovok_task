from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
from typing import AsyncGenerator
from blog_app.core.config import settings


class SessionManager:
    def __init__(self, db_url: str, echo: bool):
        self.db_url = db_url
        self.engine = create_async_engine(
            self.db_url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            class_=AsyncSession,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self.session_factory:
            raise RuntimeError("Database session factory is not initialized.")

        async with self.session_factory() as session:
            yield session


sessionmanager = SessionManager(
    db_url=settings.db_url,
    echo=settings.ECHO,
)
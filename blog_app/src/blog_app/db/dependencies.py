from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from blog_app.db.helper import sessionmanager

SessionDep = Annotated[
    AsyncSession,
    Depends(sessionmanager.get_session),
]
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
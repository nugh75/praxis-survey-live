"""Async SQLAlchemy engine + session (PostgreSQL via asyncpg)."""
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://praxis:praxis@localhost:5432/praxis_survey",
)

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def init_db():
    from . import models  # noqa: F401  (register tables)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

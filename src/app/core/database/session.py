from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .engine import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession]:
    """FastAPI dependency that provides an async database session.

    Usage:
        @router.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

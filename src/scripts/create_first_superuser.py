import asyncio
from datetime import datetime

import structlog
from sqlalchemy import select

from ..app.core import logger as _  # noqa: F401 - configures structlog/handlers
from ..app.core.auth.security import get_password_hash
from ..app.core.config import settings
from ..app.core.database.engine import AsyncSession, async_session_factory
from ..app.models.user import User

logger = structlog.get_logger(__name__)


async def create_first_user(session: AsyncSession) -> None:
    try:
        name = settings.ADMIN_NAME
        email = settings.ADMIN_EMAIL
        username = settings.ADMIN_USERNAME
        hashed_password = get_password_hash(settings.ADMIN_PASSWORD)

        query = select(User).filter_by(email=email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            # Use the existing User model instead of redefining the Table
            new_admin = User(
                name=name,
                email=email,
                username=username,
                hashed_password=hashed_password,
                is_superuser=True,
                created_at=datetime.now(),
                modified_at=datetime.now(),
            )

            session.add(new_admin)
            await session.commit()
            await logger.ainfo("Admin user created successfully.", username=username)
        else:
            await logger.ainfo("Admin user already exists.", username=username)

    except Exception as e:
        await session.rollback()
        await logger.aerror("Error creating admin user.", error=str(e))


async def main():
    async with async_session_factory() as session:
        await create_first_user(session)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

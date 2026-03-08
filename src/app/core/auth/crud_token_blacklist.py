from datetime import UTC, datetime

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.helper.crud import CRUDBase

from .token_blacklist import TokenBlacklist


class CRUDTokenBlacklist(CRUDBase[TokenBlacklist]):
    """Token-blacklist CRUD with an extra ``delete_expired`` helper."""

    async def delete_expired(self, db: AsyncSession) -> int:
        """Remove all expired tokens from the blacklist. Returns the number of deleted rows."""
        stmt = delete(self.model).where(self.model.expires_at < datetime.now(UTC).replace(tzinfo=None))
        result = await db.execute(stmt)
        await db.flush()
        return result.rowcount  # type: ignore[return-value]


crud_token_blacklist = CRUDTokenBlacklist(model=TokenBlacklist)

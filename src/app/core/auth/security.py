from typing import Literal

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from ...crud.crud_user import crud_user
from ...models.user import User


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    correct_password: bool = bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    return correct_password


def get_password_hash(password: str) -> str:
    hashed_password: str = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return hashed_password


async def authenticate_user(username_or_email: str, password: str, db: AsyncSession) -> User | Literal[False]:
    if "@" in username_or_email:
        db_user = await crud_user.get(db=db, email=username_or_email, is_deleted=False)
    else:
        db_user = await crud_user.get(db=db, username=username_or_email, is_deleted=False)

    if not db_user:
        return False

    if not await verify_password(password, db_user.hashed_password):
        return False

    return db_user

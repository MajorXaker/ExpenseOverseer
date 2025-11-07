import sqlalchemy as sa
from aiogram.types import User
from sqlalchemy.ext.asyncio import AsyncSession

import models.db_models as m
from utils.config import log


async def get_user(
    session: AsyncSession,
    user: User,
) -> int:
    return await session.scalar(
        sa.select(m.InternalUser.id).where(m.InternalUser.external_id == user.id)
    )


async def create_user(
    session: AsyncSession,
    user: User,
) -> int:
    log.info(f"Creating user {user.full_name} with external id {user.id}")
    internal_user_id = await session.scalar(
        sa.insert(m.InternalUser)
        .values(
            name=user.full_name,
            external_id=user.id,
            username=user.username,
        )
        .returning(m.InternalUser.id)
    )
    return internal_user_id

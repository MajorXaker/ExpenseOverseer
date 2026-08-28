from typing import Optional

import sqlalchemy as sa
from aiogram.types import User
from sqlalchemy.ext.asyncio import AsyncSession

import models.db_models as m
from models.enums.currency import CurrencyEnum
from utils.config import log


async def get_user(
    session: AsyncSession,
    user: User,
) -> Optional[sa.Row]:
    """Returns a row with `id` and `default_currency`, or None if not found."""
    return (
        await session.execute(
            sa.select(
                m.InternalUser.id,
                m.InternalUser.default_currency,
            ).where(m.InternalUser.external_id == user.id)
        )
    ).one_or_none()


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


async def set_default_currency(
    session: AsyncSession,
    user_id: int,
    currency: CurrencyEnum,
) -> None:
    await session.execute(
        sa.update(m.InternalUser)
        .where(m.InternalUser.id == user_id)
        .values(default_currency=currency)
    )

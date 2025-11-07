from typing import Callable, Any, Awaitable
from aiogram.types import Message

from core.user_actions import get_user, create_user
from models.dto.user_data import UserData
from utils.config import log
import sqlalchemy as sa
from models import db_models as m
from sqlalchemy.ext.asyncio import AsyncSession

class UserTranslationMiddleware:
    """
    Middleware that manages database session lifecycle.
    Opens session before handler, closes after.
    """

    async def _is_user_whitelisted(self, session: AsyncSession, username: str) -> int:
        is_user_whitelisted = await session.scalar(
            sa.select(m.UserWhitelist.id)
            .where(m.UserWhitelist.username == username)
        )
        return is_user_whitelisted

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any],
    ) -> Any:
        if not await self._is_user_whitelisted(data["session"], event.from_user.username):
            await event.answer("You are not authorized to use this bot.")
            return

        user_id = await get_user(data["session"], event.from_user)

        if not user_id:
            log.info(f"User '{event.from_user.username}' not found, but whitelisted. Creating it.")
            user_id = await create_user(data["session"], event.from_user)

        data["user_data"] = UserData(user_id=user_id, username=event.from_user.username)
        return await handler(event, data)


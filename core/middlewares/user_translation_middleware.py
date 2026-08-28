from typing import Any, Awaitable, Callable

import sqlalchemy as sa
from aiogram.types import Message, Update, User
from sqlalchemy.ext.asyncio import AsyncSession

from core.language import texts
from core.language.base import Translator
from core.user_actions import create_user, get_user
from models import db_models as m
from models.dto.user_data import UserData
from models.enums.currency import DEFAULT_CURRENCY, CurrencyEnum
from models.enums.languages import LanguageEnum
from utils.config import log


class UserTranslationMiddleware:
    """
    Middleware that created enriched user data for handlers
    """

    @staticmethod
    async def _is_user_whitelisted(session: AsyncSession, username: str) -> int:
        is_user_whitelisted = await session.scalar(
            sa.select(m.UserWhitelist.id).where(m.UserWhitelist.username == username)
        )
        return is_user_whitelisted

    @staticmethod
    async def _find_or_create_user(
        session: AsyncSession, user: User
    ) -> tuple[int, CurrencyEnum]:
        existing_user = await get_user(session, user)

        if existing_user:
            return existing_user.id, CurrencyEnum(existing_user.default_currency)

        log.info(f"User '{user.username}' not found, but whitelisted. Creating it.")
        user_id = await create_user(session, user)
        return user_id, DEFAULT_CURRENCY

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message | Update,
        data: dict[str, Any],
    ) -> Any:
        if event.message:
            user = event.message.from_user
        else:
            user = event.callback_query.from_user

        lang_code = user.language_code
        try:
            selected_language = LanguageEnum(lang_code)
        except ValueError:
            log.warning(
                f"User with not supported language code '{lang_code}'",
            )
            selected_language = LanguageEnum.EN

        translator = Translator(selected_language)

        if not await self._is_user_whitelisted(data["session"], user.username):
            await event.answer(translator(texts.general.access_denied))
            return

        user_id, default_currency = await self._find_or_create_user(
            data["session"], user
        )

        data["user_data"] = UserData(
            user_id=user_id,
            username=user.username,
            lang=Translator(selected_language),
            default_currency=default_currency,
        )
        return await handler(event, data)

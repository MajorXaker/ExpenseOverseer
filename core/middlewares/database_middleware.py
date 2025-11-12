from typing import Any, Awaitable, Callable

from aiogram.types import Message

from utils.db import get_session


class DatabaseMiddleware:
    """
    Middleware that manages database session lifecycle.
    Opens session before handler, closes after.
    """

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        async with get_session() as db_session:
            data["session"] = db_session
            return await handler(event, data)

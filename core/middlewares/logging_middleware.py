from typing import Callable, Any, Awaitable
from aiogram.types import Message
from utils.config import log

class LoggingMiddleware:
    """
    Outer middleware that logs all incoming messages.
    Executes before filters are applied.
    """

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any],
    ) -> Any:
        """
        Log incoming message and pass it to the next handler.
        """
        log.info(f"[MIDDLEWARE] Incoming message from user {event.from_user.id}: '{event.text}'")

        # Call the next handler in the chain
        return await handler(event, data)
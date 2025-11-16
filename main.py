import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.middlewares.database_middleware import DatabaseMiddleware
from core.middlewares.logging_middleware import LoggingMiddleware
from core.middlewares.user_translation_middleware import UserTranslationMiddleware
from core.routers.general_router import text_router
from core.routers.help_router import help_router
from core.routers.settings import settings_router
from core.routers.transaction import transaction_router
from utils.config import log, settings

dp = Dispatcher()
dp.update.outer_middleware(DatabaseMiddleware())
dp.message.outer_middleware(UserTranslationMiddleware())
dp.message.outer_middleware(LoggingMiddleware())

dp.include_router(transaction_router)
dp.include_router(help_router)
dp.include_router(settings_router)
dp.include_router(text_router)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=settings.TG_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    log.info(f"Starting bot v{settings.VERSION}")
    # And the run events dispatching
    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())

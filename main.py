import asyncio
import logging
import sys

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.commands_router import text_router
from core.middlewares.database_middleware import DatabaseMiddleware
from core.middlewares.logging_middleware import LoggingMiddleware
from core.middlewares.user_translation_middleware import UserTranslationMiddleware
from utils.config import settings, log
from aiogram import Bot, Dispatcher


dp = Dispatcher()
dp.message.outer_middleware(DatabaseMiddleware())
dp.message.outer_middleware(UserTranslationMiddleware())
dp.message.outer_middleware(LoggingMiddleware())

dp.include_router(text_router)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=settings.TG_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    log.info("Starting bot")
    # And the run events dispatching
    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())

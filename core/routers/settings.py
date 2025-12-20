from aiogram import F, Router
from aiogram.types import Message

settings_router = Router()


# Settings handler
@settings_router.message(F.text == "/settings")
async def settings_command(message: Message):
    await message.answer(
        "⚙️ Settings\n\n🚧 Not implemented yet. Coming soon!",
    )

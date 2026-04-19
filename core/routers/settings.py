from aiogram import F, Router
from aiogram.types import Message

from core.language import texts
from models.dto.user_data import UserData

settings_router = Router()


# Settings handler
@settings_router.message(F.text == "/settings")
async def settings_command(
    message: Message,
    user_data: UserData,
):
    text = user_data.lang(texts.settings.placeholder)
    await message.answer(text)

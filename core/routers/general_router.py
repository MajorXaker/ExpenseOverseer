from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove

from core.language import texts
from models.dto.user_data import UserData

text_router = Router()


@text_router.message(F.text == "/start")
@text_router.message(F.text == "/help")
async def help_command(
    message: Message,
    user_data: UserData,
):
    help_text = user_data.lang(texts.general.help)
    await message.answer(help_text)


@text_router.message()
async def unknown_handler(
    message: Message,
    user_data: UserData,
):
    await message.answer(
        text=user_data.lang(texts.general.wrong_command),
        reply_markup=ReplyKeyboardRemove(),
    )

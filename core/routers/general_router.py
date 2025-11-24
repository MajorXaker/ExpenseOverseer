from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardRemove

from core.routers.help_router import get_help_message

text_router = Router()


@text_router.message(F.text == "/start")
async def help_command(message: Message):
    help_text = get_help_message()
    await message.answer(help_text)


@text_router.message()
async def unknown_handler(message: Message) -> None:
    await message.answer("Wrong command", reply_markup=ReplyKeyboardRemove())

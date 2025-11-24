from aiogram.types import ReplyKeyboardMarkup


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    return None


def add_main_menu_keyboard_wrapper(func):
    async def wrapper(*args, **kwargs): ...

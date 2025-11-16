from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create the main menu keyboard"""
    kb = [
        [KeyboardButton(text="📊 Transactions"), KeyboardButton(text="⚙️ Settings")],
        [KeyboardButton(text="❓ Help")],
    ]

    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,  # Adjusts button size to fit screen
        is_persistent=True,  # Keeps keyboard visible even after use
    )
    return keyboard


def add_main_menu_keyboard_wrapper(func):
    async def wrapper(*args, **kwargs): ...

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from models.enums.currency import SUPPORTED_CURRENCIES, CurrencyEnum


def get_currency_keyboard(current: CurrencyEnum) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for currency in SUPPORTED_CURRENCIES:
        label = currency.value
        if currency == current:
            label = f"✅ {label}"
        builder.button(text=label, callback_data=f"currency_{currency.value}")

    builder.adjust(2)
    return builder.as_markup()

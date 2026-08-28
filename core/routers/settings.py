from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.keyboards.settings import get_currency_keyboard
from core.language import texts
from core.user_actions import set_default_currency
from models.dto.user_data import UserData
from models.enums.currency import CurrencyEnum

settings_router = Router()


# Settings handler
@settings_router.message(F.text == "/settings")
async def settings_command(
    message: Message,
    user_data: UserData,
):
    text = user_data.lang(
        texts.settings.current_currency,
        currency=user_data.default_currency,
    )
    keyboard = get_currency_keyboard(user_data.default_currency)
    await message.answer(text, reply_markup=keyboard)


@settings_router.callback_query(F.data.startswith("currency_"))
async def process_currency_selection(
    callback: CallbackQuery,
    session: AsyncSession,
    user_data: UserData,
):
    currency = CurrencyEnum(callback.data.removeprefix("currency_"))

    await set_default_currency(
        session=session,
        user_id=user_data.user_id,
        currency=currency,
    )

    text = user_data.lang(texts.settings.currency_updated, currency=currency)
    keyboard = get_currency_keyboard(currency)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


def back_handler_wrapper(func):
    """Removes any inline keyboard if pressed 'back' button on this keyboard"""

    async def wrapper(*args, callback: CallbackQuery, state: FSMContext, **kwargs):
        if callback.data == "back":
            await callback.message.edit_reply_markup(reply_markup=None)
            await state.clear()
        else:
            return await func(*args, callback=callback, state=state, **kwargs)

    return wrapper

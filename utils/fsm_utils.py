from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


class FSMUtils:
    @staticmethod
    def is_back(callback: CallbackQuery):
        return callback.data == "back"

    @staticmethod
    async def process_back(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_reply_markup(reply_markup=None)
        await state.clear()

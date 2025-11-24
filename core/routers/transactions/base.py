from datetime import date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.keyboards.category import get_category_keyboard
from core.transactions import (
    record_transaction,
    set_transaction_category,
)
from models.dto.parsed_message import ParsedMessage
from models.dto.transaction import Transaction
from models.dto.user_data import UserData
from models.enums.currency import CurrencyEnum
from models.enums.transaction_type import TransactionType
from utils.exceptions import InvalidAmountException

transaction_router = Router()


class CreateTransactionFSM(StatesGroup):
    after_creation_update_category = State()


@transaction_router.message(F.text.regexp(r"^([0-9.+-]+)\s+(.+)$"))
async def handle_numbered_message(
    message: Message,
    session: AsyncSession,
    user_data: UserData,
    state: FSMContext,
):
    try:
        parsed_message = ParsedMessage.from_message(message.text)
    except InvalidAmountException as e:
        await message.answer(f"Failed to record: unrecognizable amount {e}")
        return

    transaction_type = (
        TransactionType.INCOME if parsed_message.is_income else TransactionType.EXPENSE
    )

    transaction = Transaction(
        user_id=user_data.user_id,
        amount=parsed_message.amount,
        currency=CurrencyEnum.BYN,
        description=parsed_message.description,
        date=date.today(),
        transaction_type=transaction_type,
    )
    transaction_id = await record_transaction(session, transaction)
    transaction.internal_id = transaction_id

    keyboard = await get_category_keyboard(session)

    await state.set_state(CreateTransactionFSM.after_creation_update_category)
    await message.answer(
        f"Recorded: {transaction.human_readable}", reply_markup=keyboard
    )

    await state.update_data(transaction=transaction)


# Handle category selection
@transaction_router.callback_query(CreateTransactionFSM.after_creation_update_category)
async def process_category(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    await callback.message.edit_reply_markup(reply_markup=None)
    category_str = callback.data.split("_")[1]

    if category_str == "None":
        category_id = None
    else:
        category_id = int(category_str)
    if not category_id:
        await callback.answer()

    state_data = await state.get_data()
    transaction = state_data["transaction"]

    await set_transaction_category(
        session=session,
        transaction_id=transaction.internal_id,
        transaction_type=transaction.transaction_type,
        category_id=category_id,
    )

    await callback.answer()
    await state.clear()

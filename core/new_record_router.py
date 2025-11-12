from datetime import date

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.keyboards.category import get_category_keyboard
from core.message_parsing import parse_message
from core.transactions import record_transaction, set_transaction_category
from models.dto.transaction import Transaction
from models.dto.user_data import UserData
from models.enums.currency import CurrencyEnum
from models.enums.transaction_type import TransactionType
from utils.exceptions import InvalidAmountException

text_router = Router()


@text_router.message(F.text.regexp(r"^([0-9.+-]+)\s+(.+)$"))
async def handle_numbered_message(
    message: Message, session: AsyncSession, user_data: UserData, state: FSMContext
):
    try:
        parsed_message = parse_message(message.text)
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

    keyboard = await get_category_keyboard(session)
    await message.answer(
        f"Recorded: {transaction.human_readable}", reply_markup=keyboard
    )

    await state.update_data(
        dict(transaction_id=transaction_id, transaction_type=transaction_type)
    )


# Handle category selection
@text_router.callback_query(F.data.startswith("cat_"))
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
    transaction_id = state_data["transaction_id"]
    transaction_type = state_data["transaction_type"]

    await set_transaction_category(
        session=session,
        transaction_id=transaction_id,
        transaction_type=transaction_type,
        category_id=category_id,
    )

    await callback.answer()


@text_router.message()
async def unknown_handler(message: Message) -> None:
    await message.answer("Wrong command")

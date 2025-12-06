from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, ForceReply, Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.keyboards.category import get_category_keyboard
from core.keyboards.edit_transaction import (
    chose_edit_delete_transaction_keyboard,
    get_edit_choose_part_keyboard,
    get_edit_delete_pass_keyboard,
)
from core.transactions import (
    delete_transaction,
    get_last_transactions,
    get_transaction,
    set_transaction_category,
    update_description,
    update_value,
)
from models.dto.parsed_message import ParsedMessage
from models.dto.transaction import Transaction
from models.dto.user_data import UserData
from models.enums.flow_type import TransactionFlowBranchesEnum
from utils.config import log
from utils.fsm_utils import back_handler_wrapper

edit_delete_transaction_router = Router()


class EditDeleteFSM(StatesGroup):
    select_action = State()
    delete_state = State()
    edit_state = State()
    edit_select_editable_part = State()
    edit_select_part = State()
    edit_update_value = State()
    edit_update_category = State()
    edit_update_description = State()


def _make_transactions_text(transactions: list[Transaction]) -> str | None:
    text = ""
    for n, tx in enumerate(transactions, 1):
        date_text = tx.date.strftime("%Y.%m.%d")
        text += f"{n}. ({date_text}): {tx.human_readable}\n"
    return text


@back_handler_wrapper
@edit_delete_transaction_router.message(F.text == "/transactions")
async def show_transactions(
    message: Message,
    session: AsyncSession,
    user_data: UserData,
    state: FSMContext,
):
    transactions = await get_last_transactions(session, user_data.user_id, limit=5)

    if not transactions:
        await message.answer("No transactions yet.")
        return

    await state.update_data(transactions=transactions, user_id=user_data.user_id)

    # Format transactions
    text = "**Your Last 5 Transactions**\n\n"
    text += _make_transactions_text(transactions)

    keyboard = get_edit_delete_pass_keyboard()
    await state.set_state(EditDeleteFSM.select_action)
    await message.answer(text, reply_markup=keyboard)


@back_handler_wrapper
@edit_delete_transaction_router.callback_query(EditDeleteFSM.select_action)
async def process_actions_select(
    callback: CallbackQuery,
    state: FSMContext,
):
    match callback.data:
        case TransactionFlowBranchesEnum.DELETE:
            keyboard = chose_edit_delete_transaction_keyboard(
                TransactionFlowBranchesEnum.DELETE
            )
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await state.set_state(EditDeleteFSM.delete_state)
            await callback.answer(
                "⚠️ This will irreversibly delete the selected transaction!",
                show_alert=True,  # Shows as popup/alert
            )
        case TransactionFlowBranchesEnum.EDIT:
            await callback.answer("Chose transaction you want to edit")
            keyboard = chose_edit_delete_transaction_keyboard(
                TransactionFlowBranchesEnum.EDIT
            )
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await state.set_state(EditDeleteFSM.edit_state)
        case _:
            log.warning(f"Unhandled callback request '{callback.data}'")
            await callback.message.edit_reply_markup(reply_markup=None)


@back_handler_wrapper
@edit_delete_transaction_router.callback_query(EditDeleteFSM.delete_state)
async def process_delete_transaction(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    number_to_delete = int(callback.data.lstrip("delete_"))
    state_data = await state.get_data()
    selected_transaction: Transaction = state_data["transactions"][number_to_delete]

    await delete_transaction(
        session, selected_transaction.internal_id, selected_transaction.transaction_type
    )

    transactions = await get_last_transactions(session, state_data["user_id"], limit=5)

    new_text = "**Your Last 5 Transactions (updated)**\n\n"
    new_text += _make_transactions_text(transactions)

    await callback.message.edit_text(text=new_text)


@back_handler_wrapper
@edit_delete_transaction_router.callback_query(EditDeleteFSM.edit_state)
async def process_select_for_editing(
    callback: CallbackQuery,
    state: FSMContext,
):
    updated_transaction_num = int(callback.data.lstrip("edit_"))
    state_data = await state.get_data()
    transaction_to_update = state_data["transactions"][updated_transaction_num]

    await state.update_data(transaction_to_update=transaction_to_update)

    keyboard = get_edit_choose_part_keyboard()
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await state.set_state(EditDeleteFSM.edit_select_part)
    await callback.answer(
        "Chose transaction you want to edit",
    )


@back_handler_wrapper
@edit_delete_transaction_router.callback_query(EditDeleteFSM.edit_select_part)
async def process_select_part_for_editing(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    state_data = await state.get_data()
    transaction = state_data["transaction_to_update"]

    text = f"Now updating: {transaction.human_readable}"

    match callback.data:
        case "value":
            await callback.message.edit_reply_markup(reply_markup=None)
            await callback.message.reply(
                text + "\nEnter new amount:",
                reply_markup=ForceReply(
                    input_field_placeholder="50.00"  # Hint in input field
                ),
            )
            await state.set_state(EditDeleteFSM.edit_update_value)
        case "description":
            await callback.message.edit_reply_markup(reply_markup=None)
            await callback.message.reply(
                "Enter new description",
                reply_markup=ForceReply(
                    input_field_placeholder="food"  # Hint in input field
                ),
            )
            await state.set_state(EditDeleteFSM.edit_update_description)
        case "category":
            await state.set_state(EditDeleteFSM.edit_update_category)
            keyboard = await get_category_keyboard(session)
            await callback.message.edit_reply_markup(reply_markup=keyboard)


@edit_delete_transaction_router.message(EditDeleteFSM.edit_update_value)
async def process_edit_value(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    message_text = message.text
    if message_text.startswith("+"):
        message_text = message_text[1:]
    parsed_message = ParsedMessage.parse_amount(message_text)
    state_data = await state.get_data()
    transaction: Transaction = state_data["transaction_to_update"]

    updated_transaction = await update_value(
        session=session,
        transaction_id=transaction.internal_id,
        transaction_type=transaction.transaction_type,
        new_value=parsed_message,
    )
    await message.reply(
        f"Transaction Updated\n({transaction.date.strftime('%d/%m/%Y')}): {updated_transaction.human_readable}",
        reply_markup=None,
    )
    await state.clear()


@edit_delete_transaction_router.message(EditDeleteFSM.edit_update_description)
async def process_edit_description(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):

    state_data = await state.get_data()
    transaction: Transaction = state_data["transaction_to_update"]

    updated_transaction = await update_description(
        session=session,
        transaction_id=transaction.internal_id,
        transaction_type=transaction.transaction_type,
        new_description=message.text,
    )
    await message.reply(
        f"Transaction Updated\n({transaction.date.strftime('%d/%m/%Y')}): {updated_transaction.human_readable}",
        reply_markup=None,
    )
    await state.clear()


@edit_delete_transaction_router.callback_query(EditDeleteFSM.edit_update_category)
async def process_edit_category(
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

    state_data = await state.get_data()
    transaction: Transaction = state_data["transaction_to_update"]

    await set_transaction_category(
        session=session,
        transaction_id=transaction.internal_id,
        transaction_type=transaction.transaction_type,
        category_id=category_id,
    )
    updated_transaction = await get_transaction(
        session=session,
        transaction_id=transaction.internal_id,
        transaction_type=transaction.transaction_type,
    )

    await callback.message.reply(
        f"Transaction Updated\n({transaction.date.strftime('%d/%m/%Y')}): {updated_transaction.human_readable}",
        reply_markup=None,
    )
    await state.clear()

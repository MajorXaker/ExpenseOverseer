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
from core.language import texts
from core.language.base import Translator
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
from utils.config import log, settings
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


def _make_transactions_text(
    transactions: list[Transaction],
    translator: Translator,
) -> str | None:
    text = ""
    for n, tx in enumerate(transactions, 1):
        date_text = tx.date.strftime("%Y.%m.%d")
        text += f"{n}. ({date_text}): {tx.to_human_readable(translator)}\n"
    return text


@back_handler_wrapper
@edit_delete_transaction_router.message(F.text == "/modify")
async def show_transactions(
    message: Message,
    session: AsyncSession,
    user_data: UserData,
    state: FSMContext,
):
    max_transaction_qty = settings.LAST_TRANSACTIONS_QTY
    transactions = await get_last_transactions(
        session=session,
        user_id=user_data.user_id,
        limit=max_transaction_qty,
    )

    real_transactions_qty = len(transactions)

    if not transactions:
        await message.answer(user_data.lang(texts.transactions.no_transactions))
        return

    await state.update_data(transactions=transactions, user_id=user_data.user_id)

    # Format transactions
    translated_header = user_data.lang(
        texts.transactions.last_n,
        qty=real_transactions_qty,
    )
    text = translated_header + "\n\n"
    text += _make_transactions_text(transactions, user_data.lang)

    keyboard = get_edit_delete_pass_keyboard(user_data.lang)
    await state.set_state(EditDeleteFSM.select_action)
    await message.answer(text, reply_markup=keyboard)


@back_handler_wrapper
@edit_delete_transaction_router.callback_query(EditDeleteFSM.select_action)
async def process_actions_select(
    callback: CallbackQuery,
    state: FSMContext,
    user_data: UserData,
):
    state_data = await state.get_data()
    match callback.data:
        case TransactionFlowBranchesEnum.DELETE:
            keyboard = chose_edit_delete_transaction_keyboard(
                TransactionFlowBranchesEnum.DELETE,
                actions_qty=len(state_data["transactions"]),
                translator=user_data.lang,
            )
            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await state.set_state(EditDeleteFSM.delete_state)
            await callback.answer(
                user_data.lang(texts.transactions.delete.alert),
                show_alert=True,  # Shows as popup/alert
            )
        case TransactionFlowBranchesEnum.EDIT:
            await callback.answer(user_data.lang(texts.transactions.edit.choose))
            keyboard = chose_edit_delete_transaction_keyboard(
                TransactionFlowBranchesEnum.EDIT,
                actions_qty=len(state_data["transactions"]),
                translator=user_data.lang,
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
    user_data: UserData,
):
    number_to_delete = int(callback.data.lstrip("delete_"))
    state_data = await state.get_data()
    selected_transaction: Transaction = state_data["transactions"][number_to_delete]

    await delete_transaction(
        session, selected_transaction.internal_id, selected_transaction.transaction_type
    )
    transaction_qty = settings.LAST_TRANSACTIONS_QTY
    transactions = await get_last_transactions(
        session=session,
        user_id=state_data["user_id"],
        limit=transaction_qty,
    )
    translated_header = user_data.lang(
        texts.transactions.last_n_updated,
        qty=transaction_qty,
    )
    new_text = translated_header + "\n\n"
    new_text += _make_transactions_text(transactions, user_data.lang)

    await callback.message.edit_text(text=new_text)


@back_handler_wrapper
@edit_delete_transaction_router.callback_query(EditDeleteFSM.edit_state)
async def process_select_for_editing(
    callback: CallbackQuery,
    state: FSMContext,
    user_data: UserData,
):
    updated_transaction_num = int(callback.data.lstrip("edit_"))
    state_data = await state.get_data()
    transaction_to_update = state_data["transactions"][updated_transaction_num]

    await state.update_data(transaction_to_update=transaction_to_update)

    keyboard = get_edit_choose_part_keyboard(user_data.lang)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await state.set_state(EditDeleteFSM.edit_select_part)
    await callback.answer(user_data.lang(texts.transactions.edit.choose))


@back_handler_wrapper
@edit_delete_transaction_router.callback_query(EditDeleteFSM.edit_select_part)
async def process_select_part_for_editing(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user_data: UserData,
):
    state_data = await state.get_data()
    transaction = state_data["transaction_to_update"]

    text = (
        f"{user_data.lang(texts.transactions.edit.updating)}:"
        f" {transaction.to_human_readable(user_data.lang)}"
    )

    match callback.data:
        case "amount":
            await callback.message.edit_reply_markup(reply_markup=None)
            new_amount_text = user_data.lang(texts.transactions.edit.amount)
            await callback.message.reply(
                f"{text}\n{new_amount_text}:",
                reply_markup=ForceReply(
                    input_field_placeholder="50.00"  # Hint in input field
                ),
            )
            await state.set_state(EditDeleteFSM.edit_update_value)
        case "description":
            await callback.message.edit_reply_markup(reply_markup=None)
            new_description_text = user_data.lang(texts.transactions.edit.description)
            await callback.message.reply(
                f"{text}\n{new_description_text}:",
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
    user_data: UserData,
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
    success_text = user_data.lang(texts.transactions.edit.success)
    await message.reply(
        f"{success_text}\n"
        f"({transaction.date.strftime('%d/%m/%Y')}): "
        f"{updated_transaction.to_human_readable(user_data.lang)}",
        reply_markup=None,
    )
    await state.clear()


@edit_delete_transaction_router.message(EditDeleteFSM.edit_update_description)
async def process_edit_description(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user_data: UserData,
):

    state_data = await state.get_data()
    transaction: Transaction = state_data["transaction_to_update"]

    updated_transaction = await update_description(
        session=session,
        transaction_id=transaction.internal_id,
        transaction_type=transaction.transaction_type,
        new_description=message.text,
    )
    success_text = user_data.lang(texts.transactions.edit.success)
    await message.reply(
        f"{success_text}\n"
        f"({transaction.date.strftime('%d/%m/%Y')}): "
        f"{updated_transaction.to_human_readable(user_data.lang)}",
        reply_markup=None,
    )
    await state.clear()


@edit_delete_transaction_router.callback_query(EditDeleteFSM.edit_update_category)
async def process_edit_category(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user_data: UserData,
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
    success_text = user_data.lang(texts.transactions.edit.success)
    await callback.message.reply(
        f"{success_text}\n"
        f"({transaction.date.strftime('%d/%m/%Y')}): "
        f"{updated_transaction.to_human_readable(user_data.lang)}",
        reply_markup=None,
    )
    await state.clear()

from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.language import texts
from core.language.base import Translator
from models.enums.flow_type import TransactionFlowBranchesEnum


def get_edit_delete_pass_keyboard(translator: Translator):
    builder = InlineKeyboardBuilder()

    for command in TransactionFlowBranchesEnum:
        builder.button(text=command.capitalize(), callback_data=command)

    builder.button(text=translator(texts.general.back), callback_data="back")

    builder.adjust(2, 1)
    return builder.as_markup()


def chose_edit_delete_transaction_keyboard(
    flow_type: TransactionFlowBranchesEnum, actions_qty: int, translator: Translator
):
    builder = InlineKeyboardBuilder()

    if flow_type == TransactionFlowBranchesEnum.EDIT:
        text = texts.transactions.edit
    elif flow_type == TransactionFlowBranchesEnum.DELETE:
        text = texts.transactions.delete

    for n in range(0, actions_qty):
        builder.button(
            text=translator(text.button, i=n + 1),
            callback_data=f"{flow_type}_{n}",
        )
        # n+1 because ordinary users are not counting from 0

    builder.button(text=translator(texts.general.back), callback_data="back")

    row_width = 2

    button_rows = [row_width] * (actions_qty // row_width) + [
        1,
    ]

    if actions_qty % row_width != 0:
        button_rows += [actions_qty % row_width]
    if actions_qty % row_width > 0:
        button_rows.append(row_width)

    button_rows.append(1)

    builder.adjust(*button_rows)
    return builder.as_markup()


def get_edit_choose_part_keyboard(translator: Translator):
    builder = InlineKeyboardBuilder()

    builder.button(
        text=translator(texts.transactions.edit.amount_short), callback_data="amount"
    )
    builder.button(
        text=translator(texts.transactions.edit.description_short),
        callback_data="description",
    )
    builder.button(
        text=translator(texts.transactions.new.category).capitalize(),
        callback_data="category",
    )
    builder.button(text=translator(texts.general.back), callback_data="back")

    builder.adjust(2)
    return builder.as_markup()

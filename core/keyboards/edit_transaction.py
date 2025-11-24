from aiogram.utils.keyboard import InlineKeyboardBuilder

from models.enums.flow_type import TransactionFlowBranchesEnum


def get_edit_delete_pass_keyboard():
    builder = InlineKeyboardBuilder()

    for command in TransactionFlowBranchesEnum:
        builder.button(text=command.capitalize(), callback_data=command)

    builder.button(text="Back", callback_data="back")

    builder.adjust(2, 1)
    return builder.as_markup()


def chose_edit_delete_transaction_keyboard(flow_type: TransactionFlowBranchesEnum):
    builder = InlineKeyboardBuilder()

    for n in range(0, 5):
        builder.button(
            text=f"{flow_type.capitalize()} {n+1} transaction",
            callback_data=f"{flow_type}_{n}",
        )
        # n+1 because ordinary users are not counting from 0

    builder.button(text="Back", callback_data="back")

    builder.adjust(2)
    return builder.as_markup()


def get_edit_choose_part_keyboard():
    builder = InlineKeyboardBuilder()

    for command in ("value", "description", "category", "back"):
        builder.button(text=command.capitalize(), callback_data=command)

    builder.adjust(2)
    return builder.as_markup()

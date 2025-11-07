import re
from datetime import date
from decimal import Decimal

from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.transactions import record_transaction
from models.dto.transaction import Transaction
from models.dto.user_data import UserData
from models.enums.currency import CurrencyEnum
from models.enums.transaction_type import TransactionType

text_router = Router()


@text_router.message(F.text.regexp(r"^\+?([0-9.]+)\s+(.+)$"))
async def handle_numbered_message(
    message: Message,
    session: AsyncSession,
    user_data: UserData,
):
    data = re.match(
        r"^(?P<is_income>\+?)\s*(?P<amount>[0-9.]+)\s+(?P<description>.+)$",
        message.text,
    ).groupdict()

    transaction_type = (
        TransactionType.INCOME if data["is_income"] else TransactionType.EXPENSE
    )

    transaction = Transaction(
        user_id=user_data.user_id,
        amount=Decimal(data["amount"]),
        currency=CurrencyEnum.BYN,
        description=data["description"],
        date=date.today(),
        transaction_type=transaction_type,
    )
    await record_transaction(session, transaction)
    await message.answer(f"Recorded: {transaction.human_readable}")


@text_router.message()
async def unknown_handler(message: Message) -> None:
    await message.answer("Wrong command")

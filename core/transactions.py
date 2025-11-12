from typing import Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from models.dto.transaction import Transaction
from models.enums.currency import CurrencyEnum
from models.enums.transaction_type import TransactionType


def _create_insert_query(transaction: Transaction) -> sa.Insert:
    model = transaction.get_model()

    query = (
        sa.insert(model)
        .values(
            {
                model.user_id: transaction.user_id,
                model.amount: transaction.amount,
                model.currency: CurrencyEnum.BYN,  # hardcoded currency for version 0.0.1
                model.description: transaction.description,
            }
        )
        .returning(model.id)
    )

    return query


async def record_transaction(
    session: AsyncSession,
    transaction: Transaction,
):
    query = _create_insert_query(transaction)
    return await session.scalar(query)


async def set_transaction_category(
    session: AsyncSession,
    transaction_id: int,
    transaction_type: TransactionType,
    category_id: Optional[int],
):
    model = Transaction.model_from_transaction_type(transaction_type)

    await session.execute(
        sa.update(model)
        .where(model.id == transaction_id)
        .values(category_id=category_id)
    )

from models.dto.transaction import Transaction
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from models import db_models as m
from models.enums.currency import CurrencyEnum
from models.enums.transaction_type import TransactionType


def _create_insert_query(transaction: Transaction) -> sa.Insert:
    if transaction.transaction_type == TransactionType.INCOME:
        model = m.Debit
    elif transaction.transaction_type == TransactionType.EXPENSE:
        model = m.Credit
    else:
        raise ValueError(f"Unknown transaction type: {transaction.transaction_type}")

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
    return await session.execute(query)

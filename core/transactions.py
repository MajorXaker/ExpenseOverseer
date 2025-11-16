from typing import Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from models import db_models as m
from models.dto.transaction import Transaction
from models.enums.currency import CurrencyEnum
from models.enums.transaction_type import TransactionType


def _create_insert_query(transaction: Transaction) -> sa.Insert:
    model: m.Credit | m.Debit = transaction.get_model()

    query = (
        sa.insert(model)
        .values(
            {
                model.user_id: transaction.user_id,
                model.amount: transaction.amount,
                model.currency: CurrencyEnum.BYN,  # hardcoded currency for version 0.0.1
                model.description: transaction.description,
                model.transaction_date: transaction.date,
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


async def get_last_transactions(
    session: AsyncSession, user_id: int, limit: int = 5
) -> list[Transaction]:
    unionizing = [
        sa.select(
            model.id,
            model.currency,
            model.description,
            model.amount,
            model.created_at,
            sa.literal(model.__tablename__).label("operation_type"),
        ).where(model.user_id == user_id)
        for model in (m.Credit, m.Debit)
    ]
    transactions = (
        await session.execute(
            sa.union_all(*unionizing).order_by(sa.desc("created_at")).limit(limit)
        )
    ).all()

    result = []

    for row in transactions:
        val = Transaction(
            amount=row.amount,
            currency=row.currency,
            description=row.description,
            date=row.created_at.date(),
            transaction_type=(
                TransactionType.INCOME
                if row.operation_type == "debits"
                else TransactionType.EXPENSE
            ),
            user_id=user_id,
        )
        result.append(val)

    return result

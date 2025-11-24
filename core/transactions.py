from decimal import Decimal
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from models import db_models as m
from models.dto.transaction import Transaction
from models.enums.currency import CurrencyEnum
from models.enums.transaction_type import TransactionType


def _create_insert_query(transaction: Transaction) -> sa.Insert:
    model: m.Credit | m.Debit = transaction.model

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
            model.category_id,
            model.created_at,
            sa.literal(model.__tablename__).label("operation_type"),
            m.TransactionCategory.name.label("category_name"),
        )
        .outerjoin(m.TransactionCategory, model.category_id == m.TransactionCategory.id)
        .where(model.user_id == user_id)
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
            internal_id=row.id,
            category_id=row.category_id,
            category_name=row.category_name,
        )
        result.append(val)

    return result


async def delete_transaction(
    session: AsyncSession,
    transaction_id: int,
    transaction_type: TransactionType,
):
    transaction_model = Transaction.model_from_transaction_type(transaction_type)
    await session.execute(
        sa.delete(transaction_model).where(transaction_model.id == transaction_id)
    )


async def get_transaction(
    session: AsyncSession,
    transaction_id: int,
    transaction_type: TransactionType,
) -> Transaction:
    transaction_model = Transaction.model_from_transaction_type(transaction_type)
    query = (
        sa.select(
            transaction_model.id,
            transaction_model.currency,
            transaction_model.description,
            transaction_model.amount,
            transaction_model.created_at,
            transaction_model.user_id,
            transaction_model.category_id,
            m.TransactionCategory.name.label("category_name"),
        )
        .outerjoin(
            m.TransactionCategory,
            transaction_model.category_id == m.TransactionCategory.id,
        )
        .where(transaction_model.id == transaction_id)
    )
    transaction = (await session.execute(query)).one()

    val = Transaction(
        amount=transaction.amount,
        currency=transaction.currency,
        description=transaction.description,
        date=transaction.created_at.date(),
        transaction_type=transaction_type,
        user_id=transaction.user_id,
        internal_id=transaction.id,
        category_id=transaction.category_id,
        category_name=transaction.category_name,
    )

    return val


async def update_value(
    session: AsyncSession,
    transaction_id: int,
    transaction_type: TransactionType,
    new_value: Decimal,
) -> Transaction:
    model = Transaction.model_from_transaction_type(transaction_type)
    await session.execute(
        sa.update(model).where(model.id == transaction_id).values(amount=new_value)
    )
    return await get_transaction(session, transaction_id, transaction_type)


async def update_description(
    session: AsyncSession,
    transaction_id: int,
    transaction_type: TransactionType,
    new_description: str,
) -> Transaction:
    model = Transaction.model_from_transaction_type(transaction_type)
    await session.execute(
        sa.update(model)
        .where(model.id == transaction_id)
        .values(description=new_description)
    )
    return await get_transaction(session, transaction_id, transaction_type)


async def update_category(
    session: AsyncSession,
    transaction_id: int,
    transaction_type: TransactionType,
    new_category_id: int,
) -> Transaction:
    model = Transaction.model_from_transaction_type(transaction_type)
    await session.execute(
        sa.update(model)
        .where(model.id == transaction_id)
        .values(category_id=new_category_id)
    )
    return await get_transaction(session, transaction_id, transaction_type)

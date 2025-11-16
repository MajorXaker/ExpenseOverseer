import datetime
import random
from decimal import Decimal
from typing import Literal

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import models.db_models as m
from models.enums.currency import CurrencyEnum

random.seed("123456")


class Creator:
    user_counter = 0

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(
        self,
        full_name: str = None,
        external_id: int = None,
        username: str = None,
    ):
        if not full_name:
            self.user_counter += 1
            full_name = f"user_{random.randint(0, 1000)}"

        if not external_id:
            external_id = random.randint(0, 1000)

        user_id = await self.session.scalar(
            sa.insert(m.InternalUser)
            .values(
                {
                    m.InternalUser.name: full_name,
                    m.InternalUser.external_id: external_id,
                    m.InternalUser.username: username,
                }
            )
            .returning(m.InternalUser.id)
        )

        return user_id

    async def _create_transaction(
        self,
        model: Literal[m.Credit, m.Debit],
        user_id: int,
        amount: Decimal | int | float = None,
        description: str = "expense",
        category_id: int = None,
    ):
        if not amount:
            amount = Decimal(random.randint(1, 10000)) / 100
        else:
            amount = Decimal(amount)
        return await self.session.scalar(
            sa.insert(model).values(
                {
                    model.user_id: user_id,
                    model.currency: CurrencyEnum.BYN,
                    model.amount: amount,
                    model.description: description,
                    model.category_id: category_id,
                    model.transaction_date: datetime.datetime.now(),
                }
            )
        )

    async def create_credit(
        self,
        user_id: int,
        amount: Decimal | int | float = None,
        description: str = "expense",
        category_id: int = None,
    ):
        return await self._create_transaction(
            model=m.Credit,
            user_id=user_id,
            amount=amount,
            description=description,
            category_id=category_id,
        )

    async def create_debit(
        self,
        user_id: int,
        amount: Decimal | int | float = None,
        description: str = "expense",
        category_id: int = None,
    ) -> int:
        return await self._create_transaction(
            model=m.Debit,
            user_id=user_id,
            amount=amount,
            description=description,
            category_id=category_id,
        )

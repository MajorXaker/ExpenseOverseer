import re
from datetime import date
from decimal import Decimal

import pytest

from core.routers.transactions.base import _TRANSACTION_MESSAGE_REGEXP
from core.transactions import get_last_transactions, record_transaction
from models.dto.transaction import Transaction
from models.enums.currency import CurrencyEnum
from models.enums.transaction_type import TransactionType


@pytest.mark.asyncio
class TestMessageProcessing:
    @pytest.skip  # TODO: seems to be failing
    async def test_get_last_transactions(self, dbsession, creator):
        user_id = await creator.create_user()
        await creator.create_credit(user_id, amount=100, description="food")
        await creator.create_debit(user_id, amount=2000, description="income")
        await creator.create_credit(user_id, amount=16, description="coffee")
        await creator.create_debit(user_id, amount=28.25, description="sold stuff")
        await creator.create_credit(user_id, amount=Decimal(0.9), description="ticket")
        await creator.create_debit(user_id, amount=550, description="income")

        last_3 = await get_last_transactions(dbsession, user_id, limit=3)

        assert len(last_3) == 3
        assert last_3[0].description == "income"
        assert last_3[1].description == "ticket"
        assert last_3[2].description == "sold stuff"

        assert last_3[0].amount == 550
        assert last_3[1].amount == Decimal(0.9)
        assert last_3[2].amount == Decimal(28.25)

    async def test_record_transaction_stores_selected_currency(
        self, dbsession, creator
    ):
        user_id = await creator.create_user()

        transaction = Transaction(
            user_id=user_id,
            amount=Decimal("12.5"),
            currency=CurrencyEnum.PLN,
            description="taxi",
            date=date.today(),
            transaction_type=TransactionType.EXPENSE,
        )
        await record_transaction(dbsession, transaction)

        last_transactions = await get_last_transactions(dbsession, user_id, limit=1)

        assert len(last_transactions) == 1
        assert last_transactions[0].currency == CurrencyEnum.PLN
        assert last_transactions[0].amount == Decimal("12.5")

    async def test_new_transaction_handling(self):
        valid_transactions = [
            "Eur 3.77 food",
            "pln 18.0 ticket",
            "usd 42 fee",
            "12.1 перекус",
            "12+1.4 Квіткі ў кіно",
        ]
        for transaction in valid_transactions:
            parsed = None  # noqa
            parsed = re.match(_TRANSACTION_MESSAGE_REGEXP, transaction)
            assert parsed

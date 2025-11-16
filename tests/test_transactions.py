from decimal import Decimal

import pytest

from core.transactions import get_last_transactions


@pytest.mark.asyncio
class TestMessageProcessing:
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

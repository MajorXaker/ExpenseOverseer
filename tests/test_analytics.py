from datetime import datetime
from decimal import Decimal

import pytest
from freezegun import freeze_time

from core.charts.pie_by_category import CategoryPieChartCreator


@pytest.mark.asyncio
class TestAnalytics:
    async def test_get_last_month_spendings(self, dbsession, creator):
        user_id = await creator.create_user()
        category_a_id = await creator.create_category("category_a")
        category_b_id = await creator.create_category("category_b")

        await creator.create_credit(
            user_id=user_id,
            category_id=category_a_id,
            amount=100,
            description="food",
            created_at=datetime(year=2021, month=1, day=1),
        )
        await creator.create_credit(
            user_id=user_id,
            category_id=category_a_id,
            amount=3,
            description="coffee",
            created_at = datetime(year=2021, month=1, day=15),
        )
        await creator.create_credit(
            user_id=user_id,
            category_id=category_b_id,
            amount=80,
            description="fuel",
            created_at=datetime(year=2021, month=1, day=5),
        )
        await creator.create_credit(
            user_id=user_id,
            category_id=category_b_id,
            amount=83,
            description="car stuff",
            created_at=datetime(year=2021, month=1, day=28),
        )
        # these transactions should not be shown in statistics
        await creator.create_credit(
            user_id=user_id,
            category_id=category_b_id,
            amount=400,
            description="new wheels",
            created_at=datetime(year=2020, month=12, day=2),
        )
        await creator.create_credit(
            user_id=user_id,
            category_id=category_b_id,
            amount=400,
            description="new wheels again :(",
            created_at=datetime(year=2021, month=2, day=2),
        )

        with freeze_time(datetime(year=2021, month=2, day=2)):
            stats_creator = CategoryPieChartCreator(
                session=dbsession,
                user_id=user_id,
            )
            await stats_creator.fetch_last_month()

        assert stats_creator.data == {'Category_a': Decimal('103'), 'Category_b': Decimal('163')}

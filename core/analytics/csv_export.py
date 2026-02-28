import csv
from collections import defaultdict
from datetime import datetime
from io import StringIO

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import models.db_models as m
from core.analytics.utils import get_month_window


class MonthlySpendingCSVExporter:
    def __init__(
        self,
        session: AsyncSession,
        user_id: int,
    ):
        self.session = session
        self.user_id = user_id
        self.data: list = []
        self._month_start: datetime | None = None

    async def fetch_previous_month(self):
        """Fetch all credit transactions for the previous month."""
        self.data = []

        start, end = get_month_window(months_ago=1)
        self._month_start = start

        query = (
            sa.select(
                m.Credit.amount,
                m.Credit.transaction_date,
                m.Credit.category_id,
                m.TransactionCategory.name.label("category_name"),
                m.Credit.description,
            )
            .outerjoin(
                m.TransactionCategory,
                m.Credit.category_id == m.TransactionCategory.id,
            )
            .where(
                m.Credit.user_id == self.user_id,
                m.Credit.transaction_date >= start,
                m.Credit.transaction_date < end,
            )
            .order_by(m.Credit.transaction_date.asc())
        )

        result = await self.session.execute(query)
        self.data = result.all()

    def export_as_bytes(self) -> bytes:
        """Export fetched data as UTF-8 encoded CSV bytes."""
        if not self.data:
            raise ValueError("No data available. Call fetch_previous_month() first.")

        buffer = StringIO()
        writer = csv.writer(buffer, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(["date", "amount", "category", "description"])

        for record in self.data:
            writer.writerow(
                [
                    record.transaction_date.strftime("%Y-%m-%d"),
                    round(record.amount, 2),
                    record.category_name.capitalize()
                    if record.category_name
                    else "Unknown",
                    record.description,
                ]
            )

        return buffer.getvalue().encode("utf-8")

    def export_daily_summary_as_bytes(self) -> bytes:
        """Export daily aggregated totals as UTF-8 encoded CSV bytes."""
        if not self.data:
            raise ValueError("No data available. Call fetch_previous_month() first.")

        daily: dict[str, float] = defaultdict(float)
        for record in self.data:
            day = record.transaction_date.strftime("%Y-%m-%d")
            daily[day] += record.amount

        buffer = StringIO()
        writer = csv.writer(buffer, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(["date", "total_amount"])

        for day in sorted(daily):
            writer.writerow([day, round(daily[day], 2)])

        return buffer.getvalue().encode("utf-8")

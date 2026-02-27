from collections import defaultdict
from datetime import datetime
from io import BytesIO

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import models.db_models as m
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from core.charts import get_colors
from core.charts.utils import days_in_month, get_month_window


class CumulativeSpendingChartCreator:
    def __init__(
        self,
        session: AsyncSession,
        user_id: int,
    ):
        self.session = session
        self.user_id = user_id

        self.base_query = sa.select(
            m.Credit.amount,
            m.Credit.transaction_date,
        ).where(m.Credit.user_id == user_id)

        self.data: dict[int, list] = {}  # month number -> list of records

    @staticmethod
    def _daily_cumsum(
        records: list, days_in_month: int
    ) -> tuple[list[int], list[float]]:
        """Aggregate records by day and return cumulative sum series."""
        daily: dict[int, float] = defaultdict(float)
        for record in records:
            daily[record.transaction_date.day] += float(record.amount)

        days = list(range(1, days_in_month + 1))
        cumsum = 0.0
        cum_values = []
        for d in days:
            cumsum += daily.get(d, 0.0)
            cum_values.append(round(cumsum, 2))

        return days, cum_values

    async def fetch_current_and_previous_month(self):
        """Fetch data for the current and previous month."""
        self.data = {}
        await self._fetch_month(months_ago=0)
        await self._fetch_month(months_ago=1)

    async def _fetch_month(self, months_ago: int):
        start, end = get_month_window(months_ago=months_ago)
        query = self.base_query.where(
            m.Credit.transaction_date >= start,
            m.Credit.transaction_date < end,
        )
        result = await self.session.execute(query)
        records = result.all()

        month_number = start.month
        self.data[month_number] = records

    def chart_as_bytes(self) -> bytes:
        if not self.data:
            raise ValueError(
                "No data available. Call fetch_current_and_previous_month() first."
            )

        colors = get_colors(len(self.data))
        fig, ax = plt.subplots(figsize=(12, 5), facecolor="#1a1a2e", dpi=100)
        ax.set_facecolor("#1a1a2e")

        for color, (month_num, records) in zip(colors, sorted(self.data.items())):
            month_start, _ = get_month_window(
                months_ago=(datetime.now().month - month_num) % 12
            )
            days_count = days_in_month(month_start.year, month_start.month)
            days, cum_values = self._daily_cumsum(records, days_count)

            label = month_start.strftime("%B %Y")
            ax.plot(days, cum_values, linewidth=2, label=label, color=color)

        ax.grid(True, color="#444466", linewidth=0.5, linestyle="--")
        ax.set_axisbelow(True)

        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.spines[:].set_color("#444466")

        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, _: str(int(x)) if int(x) % 2 != 0 else "")
        )

        ax.set_xlabel("Day of Month", color="white")
        ax.set_ylabel("Cumul. (BYN)", color="white")
        ax.set_title(
            "Cumulative Spending by Day",
            fontsize=24,
            color="white",
            weight="bold",
            pad=20,
        )

        ax.legend(
            facecolor="#2a2a4e",
            edgecolor="#444466",
            labelcolor="white",
            loc="upper left",
        )

        buffer = BytesIO()
        plt.savefig(
            buffer,
            format="png",
            bbox_inches="tight",
            facecolor="#1a1a2e",
            edgecolor="none",
            pad_inches=0.3,
            dpi=100,
        )
        buffer.seek(0)
        plt.close(fig)

        return buffer.getvalue()

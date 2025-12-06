from datetime import datetime
from io import BytesIO

import matplotlib.pyplot as plt
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import models.db_models as m
from core.charts import get_colors


def get_month_window(months_ago: int = 0) -> tuple[datetime, datetime]:
    """
    Calculate month boundaries in pure Python.
    Returns (start_datetime, end_datetime) for the target month.

    Args:
        months_ago: 0 = current month, 1 = previous month, etc.

    Returns:
        Tuple of (month_start, month_end) as datetime objects
    """
    now = datetime.now()

    # Calculate target month by subtracting months
    year = now.year
    month = now.month

    # Subtract months_ago months
    month -= months_ago
    while month <= 0:
        month += 12
        year -= 1

    # First day of target month at midnight
    month_start = datetime(year, month, 1, 0, 0, 0)

    # First day of next month at midnight (exclusive end)
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    month_end = datetime(next_year, next_month, 1, 0, 0, 0)

    return month_start, month_end


class CategoryPieChartCreator:

    def __init__(
            self,
            session: AsyncSession,
            user_id: int,
    ):
        self.session = session
        self.user_id = user_id

        self.base_query = (
            sa.select(
                m.TransactionCategory.name.label("category_name"),
                sa.func.sum(m.Credit.amount).label("sum"),
            )
            .outerjoin(
                m.Credit,
                m.Credit.category_id == m.TransactionCategory.id,
                full=True,
            )
            .group_by(m.TransactionCategory.name)
            .where(m.Credit.user_id == user_id)
        )

        self.data = None

    async def fetch_last_month(self):
        self.data = None
        await self._monthly(is_current=False)

    async def fetch_current_month(self):
        self.data = None
        await self._monthly(is_current=True)

    async def _monthly(self, is_current: bool = False):
        start, end = get_month_window(
            months_ago=0 if is_current else 1,
        )

        query = self.base_query.where(
            m.Credit.user_id == self.user_id,
            m.Credit.created_at >= start,
            m.Credit.created_at < end,
        )

        data = await self.session.execute(query)

        self.data = {
            line.category_name.capitalize() if line.category_name else "Unknown": line.sum
            for line in data
        }

    def chart_as_bytes(self) -> bytes:
        if not self.data:
            raise ValueError("No data available. Call fetch_last_month() or fetch_current_month() first.")

        # Prepare data
        labels = list(self.data.keys())
        values = list(self.data.values())
        categories_qty = len(self.data)
        colors = get_colors(categories_qty)

        # Create figure and axis
        fig, ax = plt.subplots(
            figsize=(10, 8),
            facecolor='#1a1a1a',  # Dark background
            dpi=100
        )
        ax.set_facecolor('#1a1a1a')

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values,
            labels=None,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops={'edgecolor': '#000000', 'linewidth': 1.5},
            textprops={
                'fontsize': 11,
                'weight': 'bold',
                'color': '#FFFFFF'
            }
        )

        legend_labels = [f"{name}: {amount:.2f}" for name, amount in zip(labels, values)]
        ax.legend(
            wedges,
            legend_labels,
            title="Categories",
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            borderaxespad=0.0,
            fontsize=10,
            title_fontsize=11,
        )

        # Style percentage text
        for autotext in autotexts:
            autotext.set_color('#000000')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')

        # Add title
        ax.set_title(
            'Monthly Expenses Breakdown',
            fontsize=24,
            color='#FFFFFF',
            weight='bold',
            pad=20
        )

        # Convert to bytes
        buffer = BytesIO()
        plt.savefig(
            buffer,
            format='png',
            bbox_inches='tight',
            facecolor='#1a1a1a',
            edgecolor='none',
            pad_inches=0.3,
            dpi=100
        )
        buffer.seek(0)
        plt.close(fig)

        return buffer.getvalue()
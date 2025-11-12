import sqlalchemy as sa
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

import models.db_models as m


async def get_category_keyboard(session: AsyncSession):
    categories = await session.execute(
        sa.select(
            m.TransactionCategory.id,
            m.TransactionCategory.name,
        )
    )

    builder = InlineKeyboardBuilder()

    unknown_category = type("UnknownCategory", (), {"name": "Unknown", "id": None})

    for category in (unknown_category, *categories):
        builder.button(
            text=category.name.capitalize(), callback_data=f"cat_{category.id}"
        )

    builder.adjust(2)  # 2 buttons per row
    return builder.as_markup()

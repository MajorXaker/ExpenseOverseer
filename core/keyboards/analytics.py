from enum import StrEnum

from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.language import texts
from core.language.base import Translator


class ButtonMeta(StrEnum):
    analytics_pie = "Last Month Pie"
    analytics_chart = "Last 2 Month Cumulative"
    analytics_csv = "Last Month CSV"


def get_analytics_initial_keyboard(translator: Translator):
    builder = InlineKeyboardBuilder()

    builder.button(
        text=translator(texts.analytics.analytics_pie),
        callback_data="analytics_pie",
    )
    builder.button(
        text=translator(texts.analytics.analytics_chart),
        callback_data="analytics_chart",
    )
    builder.button(
        text=translator(texts.analytics.analytics_csv),
        callback_data="analytics_csv",
    )
    builder.button(
        text=translator(texts.general.back),
        callback_data="back",
    )

    builder.adjust(2, 1, 1)
    return builder.as_markup()

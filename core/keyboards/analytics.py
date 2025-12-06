from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_analytics_initial_keyboard():
    builder = InlineKeyboardBuilder()


    builder.button(text="Last Month Pie", callback_data='analytics_pie')
    builder.button(text="Last Month CSV", callback_data='analytics_csv')
    builder.button(text="Back", callback_data="back")

    builder.adjust(2, 1)
    return builder.as_markup()
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.analytics.charts import (
    CategoryPieChartCreator,
    CumulativeSpendingChartCreator,
)
from core.analytics.csv_export import MonthlySpendingCSVExporter
from core.analytics.utils import get_month_window
from core.keyboards.analytics import get_analytics_initial_keyboard
from models.dto.user_data import UserData
from utils.config import log
from utils.fsm_utils import back_handler_wrapper

analytics_router = Router()


class AnalyticsFSM(StatesGroup):
    analytics_initial = State()


@analytics_router.message(F.text == "/analytics")
async def help_command(
    message: Message,
    user_data: UserData,
    state: FSMContext,
):
    keyboard = get_analytics_initial_keyboard()
    await state.set_state(AnalyticsFSM.analytics_initial)
    await state.update_data(user_data=user_data)

    text = "Analytical data could be shown as chart or exported into csv"
    await message.answer(text, reply_markup=keyboard)


@back_handler_wrapper
@analytics_router.callback_query(AnalyticsFSM.analytics_initial)
async def process_actions_select(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    state_data = await state.get_data()
    await callback.message.edit_reply_markup(reply_markup=None)
    match callback.data:
        case "analytics_pie":
            pie_chart_creator = CategoryPieChartCreator(
                session=session,
                user_id=state_data["user_data"].user_id,
            )
            await pie_chart_creator.fetch_last_month()
            image_bytes = pie_chart_creator.chart_as_bytes()

            tg_file = BufferedInputFile(image_bytes, filename="chart.jpg")
            await callback.message.bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=tg_file,
            )
        case "analytics_chart":
            chart_creator = CumulativeSpendingChartCreator(
                session=session,
                user_id=state_data["user_data"].user_id,
            )
            await chart_creator.fetch_current_and_previous_month()
            image_bytes = chart_creator.chart_as_bytes()

            tg_file = BufferedInputFile(image_bytes, filename="chart.jpg")
            await callback.message.bot.send_photo(
                chat_id=callback.message.chat.id,
                photo=tg_file,
            )
        case "analytics_csv":
            csv_creator = MonthlySpendingCSVExporter(
                session=session,
                user_id=state_data["user_data"].user_id,
            )
            await csv_creator.fetch_previous_month()
            data = csv_creator.export_as_bytes()

            previous_month_start, _ = get_month_window(1)
            file_name = f"transactions {previous_month_start.strftime('%Y %b')}.csv"

            tg_file = BufferedInputFile(data, filename=file_name)
            await callback.message.bot.send_document(
                chat_id=callback.message.chat.id,
                document=tg_file,
            )

            await callback.answer("TBD")
        case _:
            log.warning(f"Unhandled callback request '{callback.data}'")
    await state.clear()

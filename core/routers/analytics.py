from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from core.charts.pie_by_category import CategoryPieChartCreator
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
    match callback.data:
        case "analytics_pie":
            await callback.message.edit_reply_markup(reply_markup=None)


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
            await state.clear()

        case "analytics_csv":
            await callback.answer("TBD")
            await callback.message.edit_reply_markup(reply_markup=None)
            await state.clear()
        case _:
            log.warning(f"Unhandled callback request '{callback.data}'")
            await callback.message.edit_reply_markup(reply_markup=None)
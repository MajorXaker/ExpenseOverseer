from aiogram import F, Router
from aiogram.types import Message

from core.keyboards.main_menu import get_main_menu_keyboard

help_router = Router()


def get_help_message() -> str:
    help_text = (
        "❓ **How to Use Expense Income Tracker**\n\n"
        "**Adding an Expense:**\n"
        "1. Enter the monetary amount (e.g., 50) and a description (e.g., 'Lunch at restaurant')\n"
        "It should look like this:\n"
        "```50.45 Food\n12+1.4 Cinema Tickets\n70-28 Shop\n+500+25.5 Salary```\n"
        "You could start with + to store data as income\n"
        "Also you could use basic arithmetics (plus and minus) to calculate value\n"
        "2. Select a category from the buttons\n"
        "3. Done! Your transaction is saved.\n\n"
        "**View Transactions:**\n"
        "Press the '/transactions' button to see your recent expenses.\n\n"
        "**Settings:**\n"
        "Press the '/settings' button (coming soon)."
    )
    return help_text


# Help handler
@help_router.message(F.text == "/help")
async def help_command(message: Message):
    help_text = get_help_message()
    await message.answer(help_text, reply_markup=get_main_menu_keyboard())

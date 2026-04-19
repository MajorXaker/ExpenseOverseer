from aiogram import Bot
from aiogram.types import BotCommand

from core.language import texts
from models.enums.languages import LanguageEnum
from utils.config import log

COMMANDS = [
    "modify",
    "analytics",
    "settings",
    "help",
]


def build_commands(locale: LanguageEnum) -> list[BotCommand]:
    commands = []
    for command_text in COMMANDS:
        command = getattr(texts.commands, command_text)
        if not command:
            log.error(f"Command description for '{command_text}' not found")
            continue

        description = getattr(command, locale)
        if not description:
            log.error(
                f"Command translation for '{command_text}' into '{locale}' not found"
            )
            continue

        command = BotCommand(command=f"/{command_text}", description=description)
        commands.append(command)
    return commands


async def init_commands(bot: Bot) -> None:
    await bot.set_my_commands(build_commands(LanguageEnum.EN))
    await bot.set_my_commands(
        build_commands(LanguageEnum.EN), language_code=LanguageEnum.EN
    )
    await bot.set_my_commands(
        build_commands(LanguageEnum.RU), language_code=LanguageEnum.RU
    )
    await bot.set_my_commands(
        build_commands(LanguageEnum.BE), language_code=LanguageEnum.BE
    )

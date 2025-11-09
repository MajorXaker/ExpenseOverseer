import re
from decimal import Decimal

from models.dto.parsed_message import ParsedMessage
from utils.exceptions import InvalidAmountException


def parse_message(message_text: str) -> ParsedMessage:
    is_income = message_text.startswith("+")
    if is_income:
        message_text = message_text[1:]

    raw_amount, description = message_text.split(" ", 1)

    parsed_amount = re.findall(r'[+-]?[\d.]+', raw_amount)

    if not parsed_amount:
        raise InvalidAmountException(raw_amount)

    summed = sum(Decimal(item) for item in parsed_amount)

    return ParsedMessage(
        amount=summed,
        description=description,
        is_income=is_income,
    )

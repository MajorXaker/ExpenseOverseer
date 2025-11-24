import re
from decimal import Decimal

from pydantic import BaseModel

from utils.exceptions import InvalidAmountException


class ParsedMessage(BaseModel):
    is_income: bool = False
    amount: Decimal
    description: str

    @staticmethod
    def parse_amount(value: str) -> Decimal:
        parsed_amount = re.findall(r"[+-]?[\d.]+", value)

        if not parsed_amount:
            raise InvalidAmountException(value)

        summed = sum(Decimal(item) for item in parsed_amount)
        return summed

    @classmethod
    def from_message(cls, message_text: str) -> "ParsedMessage":
        is_income = message_text.startswith("+")
        if is_income:
            message_text = message_text[1:]

        raw_amount, description = message_text.split(" ", 1)
        summed = cls.parse_amount(raw_amount)

        return cls(
            amount=summed,
            description=description,
            is_income=is_income,
        )

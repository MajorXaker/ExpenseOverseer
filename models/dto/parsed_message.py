import re
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from models.enums.currency import SUPPORTED_CURRENCIES, CurrencyEnum
from utils.exceptions import InvalidAmountException

_SUPPORTED_CURRENCY_CODES = {currency.value for currency in SUPPORTED_CURRENCIES}


class ParsedMessage(BaseModel):
    is_income: bool = False
    amount: Decimal
    description: str
    # Per-transaction currency override, e.g. "pln 12.5 taxi".
    # None means "use the user's default currency".
    currency: Optional[CurrencyEnum] = None

    @staticmethod
    def parse_amount(value: str) -> Decimal:
        parsed_amount = re.findall(r"[+-]?[\d.]+", value)

        if not parsed_amount:
            raise InvalidAmountException(value)

        summed = sum(Decimal(item) for item in parsed_amount)
        return summed

    @classmethod
    def from_message(cls, message_text: str) -> "ParsedMessage":
        currency = None
        first_token, _, remainder = message_text.partition(" ")
        if first_token.upper() in _SUPPORTED_CURRENCY_CODES:
            currency = CurrencyEnum(first_token.upper())
            message_text = remainder

        is_income = message_text.startswith("+")
        if is_income:
            message_text = message_text[1:]

        raw_amount, description = message_text.split(" ", 1)
        summed = cls.parse_amount(raw_amount)

        return cls(
            amount=summed,
            description=description,
            is_income=is_income,
            currency=currency,
        )

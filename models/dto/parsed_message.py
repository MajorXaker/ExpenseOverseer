from decimal import Decimal

from pydantic import BaseModel


class ParsedMessage(BaseModel):
    is_income: bool = False
    amount: Decimal
    description: str

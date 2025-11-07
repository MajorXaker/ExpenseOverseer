from decimal import Decimal

from pydantic import BaseModel
from datetime import date

from models.enums.currency import CurrencyEnum
from models.enums.transaction_type import TransactionType


class Transaction(BaseModel):
    user_id: int
    amount: Decimal
    currency: CurrencyEnum
    description: str
    date: date
    transaction_type: TransactionType

    @property
    def human_readable(self) -> str:
        return (
            "expense " if TransactionType.EXPENSE else "income "
        ) + f"{self.amount} {self.currency}, description: \"{self.description}\""

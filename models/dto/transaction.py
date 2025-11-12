from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from models import db_models as m
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
            "expense "
            if self.transaction_type == TransactionType.EXPENSE
            else "income "
        ) + f'{self.amount} {self.currency}, description: "{self.description}"'

    @staticmethod
    def model_from_transaction_type(
        transaction_type: TransactionType,
    ) -> Literal[m.Credit | m.Debit]:
        if transaction_type == TransactionType.INCOME:
            return m.Debit
        elif transaction_type == TransactionType.EXPENSE:
            return m.Credit
        else:
            raise ValueError(f"Unknown transaction type: {transaction_type}")

    def get_model(self) -> Literal[m.Credit | m.Debit]:
        return self.model_from_transaction_type(self.transaction_type)

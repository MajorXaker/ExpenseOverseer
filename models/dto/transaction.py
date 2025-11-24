from datetime import date
from decimal import Decimal
from typing import Literal, Optional

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

    internal_id: Optional[int] = (
        None  # database id, filled only for existing transactions
    )
    category_id: Optional[int] = None
    category_name: Optional[str] = None

    @property
    def human_readable(self) -> str:
        text = (
            "expense "
            if self.transaction_type == TransactionType.EXPENSE
            else "income "
        )
        text += f'{self.amount} {self.currency} "{self.description}"'

        if self.category_name:
            text += f' category: "{self.category_name}"'
        return text

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

    @property
    def model(self) -> Literal[m.Credit | m.Debit]:
        return self.model_from_transaction_type(self.transaction_type)

    @staticmethod
    def type_from_model(model: Literal[m.Credit | m.Debit]) -> TransactionType:
        return TransactionType.EXPENSE if model == m.Credit else TransactionType.INCOME

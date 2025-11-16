import sqlalchemy as sa

from models import db_models as m
from models.db_models.base import Model, RecordTimestampFields
from models.enums.currency import CurrencyEnum


class AbstractTransaction(RecordTimestampFields):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(m.InternalUser.id), nullable=False)

    amount = sa.Column(sa.DECIMAL, nullable=False)
    currency = sa.Column(
        sa.String(3),
        nullable=False,
        default=CurrencyEnum.BYN,
        server_default=CurrencyEnum.BYN,
    )
    transaction_date = sa.Column(
        sa.DateTime,
        nullable=False,
    )

    description = sa.Column(sa.Text, nullable=False)
    category_id = sa.Column(
        sa.ForeignKey(m.TransactionCategory.id, ondelete="SET NULL"),
        nullable=True,
    )


class Debit(Model, AbstractTransaction):
    __tablename__ = "debits"


class Credit(Model, AbstractTransaction):
    __tablename__ = "credits"

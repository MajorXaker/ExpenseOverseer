import sqlalchemy as sa

from models.db_models.base import Model


class TransactionCategory(Model):
    __tablename__ = "transaction_categories"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.Text, nullable=False)

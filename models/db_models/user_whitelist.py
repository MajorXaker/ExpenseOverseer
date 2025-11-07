import sqlalchemy as sa

from models.db_models.base import Model


class UserWhitelist(Model):
    __tablename__ = "users_whitelist"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    username = sa.Column(sa.Text, unique=True, nullable=False)

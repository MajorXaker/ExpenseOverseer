import sqlalchemy as sa

from models.db_models.base import Model, RecordTimestampFields


class InternalUser(Model, RecordTimestampFields):
    __tablename__ = "internal_users"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, index=True, nullable=False)
    username = sa.Column(sa.String, nullable=True)

    external_id = sa.Column(sa.Integer, unique=True, nullable=False)

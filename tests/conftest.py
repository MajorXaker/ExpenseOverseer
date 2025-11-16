from typing import Any, AsyncGenerator

import pytest_asyncio
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from models import db_models as m
from tests.creator import Creator
from utils.config import settings as st

db_url = (
    "postgresql+asyncpg://"
    f"{st.DATABASE_USER}:"
    f"{st.DATABASE_PASSWORD}@"
    f"{st.DATABASE_HOST}:"
    f"{st.DATABASE_PORT}/"
    f"{st.DATABASE_DB}"
)


def check_test_db():
    if (
        st.DATABASE_HOST not in ("localhost", "127.0.0.1", "postgres")
        or "amazonaws" in st.DATABASE_HOST
    ):
        print(db_url)
        raise Exception("Use local database only!")


async def drop_everything(engine: Engine | AsyncEngine):
    # db may resist dropping all due to internal relations to each other
    # so we first locate all foreign keys and tables
    # then we drop all constraints first
    # and then all tables
    from sqlalchemy.schema import DropConstraint, DropTable

    tables = []
    all_fkeys = []
    for model in m.Model.metadata.sorted_tables:
        tables.append(model.name)
        for column in model.columns._all_columns:
            if not column.foreign_keys:
                continue
            for foreign_key in column.foreign_keys:
                all_fkeys.append(foreign_key)

    async with engine.begin() as con:
        for fkey in all_fkeys:
            con.execute(DropConstraint(fkey))

        for table in tables:
            con.execute(DropTable(table))


@pytest_asyncio.fixture(scope="function")
async def engine():
    check_test_db()
    print(db_url)
    e = create_async_engine(db_url, echo=False, max_overflow=25)
    try:
        async with e.begin() as con:
            await con.run_sync(m.Model.metadata.create_all)

        yield e
    finally:
        # contents of this function does not work outside of it
        await drop_everything(e)


@pytest_asyncio.fixture(scope="function")
async def dbsession(engine) -> AsyncGenerator[AsyncSession, Any]:
    async with AsyncSession(bind=engine) as session:
        yield session


@pytest_asyncio.fixture(scope="function")
def creator(dbsession) -> Creator:
    return Creator(dbsession)

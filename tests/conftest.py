import asyncio

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from models import db_models as m
from utils.config import settings as st

from .creator import Creator

db_url = (
    "postgresql+asyncpg://"
    f"{st.DATABASE_USER}:"
    f"{st.DATABASE_PASSWORD}@"
    f"{st.DATABASE_HOST}:"
    f"{st.DATABASE_PORT}/"
    f"{st.DATABASE_DB}"
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


def check_test_db():
    if (
        st.DATABASE_HOST not in ("localhost", "127.0.0.1", "postgres")
        or "amazonaws" in st.DATABASE_HOST
    ):
        print(db_url)
        raise Exception("Use local database only!")


async def drop_everything(engine: Engine):
    # db may resist dropping all due to internal relations to each other
    # so we first locate all foreign keys and tables
    # then we drop all constraints first
    # and then all tables
    from sqlalchemy.schema import (
        DropConstraint,
        DropTable,
    )

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


@pytest.fixture(scope="session")
async def engine():
    check_test_db()

    e = create_async_engine(db_url, echo=False, max_overflow=25)

    try:
        async with e.begin() as con:
            await con.run_sync(m.Model.metadata.create_all)

        yield e
    finally:
        # contents of this function does not work outside of it
        await drop_everything(e)


@pytest.fixture
async def dbsession(engine) -> AsyncSession:
    async with AsyncSession(bind=engine) as session:
        yield session


@pytest.fixture
def creator(dbsession) -> Creator:
    return Creator(dbsession)

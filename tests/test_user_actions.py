from types import SimpleNamespace

import pytest

from core.user_actions import create_user, get_user, set_default_currency
from models.enums.currency import CurrencyEnum


def _fake_user(external_id: int, username: str = "alex") -> SimpleNamespace:
    return SimpleNamespace(
        id=external_id,
        username=username,
        full_name="Alex",
    )


@pytest.mark.asyncio
class TestUserActions:
    async def test_new_user_defaults_to_byn(self, dbsession):
        tg_user = _fake_user(external_id=111)

        user_id = await create_user(dbsession, tg_user)
        row = await get_user(dbsession, tg_user)

        assert row.id == user_id
        assert CurrencyEnum(row.default_currency) == CurrencyEnum.BYN

    async def test_get_user_returns_none_for_unknown_user(self, dbsession):
        tg_user = _fake_user(external_id=222)

        row = await get_user(dbsession, tg_user)

        assert row is None

    async def test_set_default_currency_updates_selection(self, dbsession):
        tg_user = _fake_user(external_id=333)
        user_id = await create_user(dbsession, tg_user)

        await set_default_currency(dbsession, user_id, CurrencyEnum.EUR)
        row = await get_user(dbsession, tg_user)

        assert CurrencyEnum(row.default_currency) == CurrencyEnum.EUR

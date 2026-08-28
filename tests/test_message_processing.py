from decimal import Decimal as D

import pytest

from models.dto.parsed_message import ParsedMessage
from models.enums.currency import CurrencyEnum


@pytest.mark.asyncio
class TestMessageProcessing:
    @pytest.mark.parametrize(
        "message_text, expected_result",
        (
            ("25 coffee", ParsedMessage(amount=D(25), description="coffee")),
            ("19.34 coffee", ParsedMessage(amount=D("19.34"), description="coffee")),
            ("25.5 coffee", ParsedMessage(amount=D("25.5"), description="coffee")),
            (
                "+50 zarplata",
                ParsedMessage(amount=D(50), description="zarplata", is_income=True),
            ),
            (
                "+50.11 zarplata",
                ParsedMessage(
                    amount=D("50.11"), description="zarplata", is_income=True
                ),
            ),
            ("100-25 food", ParsedMessage(amount=D(75), description="food")),
            ("100-25-15 food", ParsedMessage(amount=D(60), description="food")),
            (
                "100-25-15+5 food and stuff",
                ParsedMessage(amount=D(65), description="food and stuff"),
            ),
            (
                "50+25-30+2.5 food and stuff",
                ParsedMessage(amount=D("47.5"), description="food and stuff"),
            ),
        ),
        ids=(
            "simple",
            "amount_with_decimal_part",
            "amount_with_largest_decimal_part",
            "income",
            "income_with_decimal",
            "calculated_items_simple",
            "double_calculated",
            "advanced_calculated",
            "advanced_calculated_mkII",
        ),
    )
    async def test_message_parsing(
        self, message_text: str, expected_result: tuple[D, str]
    ):
        processed_result = ParsedMessage.from_message(message_text)
        assert processed_result == expected_result

    @pytest.mark.parametrize(
        "message_text, expected_result",
        (
            (
                "pln 12.5 taxi",
                ParsedMessage(
                    amount=D("12.5"), description="taxi", currency=CurrencyEnum.PLN
                ),
            ),
            (
                "PLN 12.5 taxi",
                ParsedMessage(
                    amount=D("12.5"), description="taxi", currency=CurrencyEnum.PLN
                ),
            ),
            (
                "eur 50 hotel",
                ParsedMessage(
                    amount=D(50), description="hotel", currency=CurrencyEnum.EUR
                ),
            ),
            (
                "usd +100 salary",
                ParsedMessage(
                    amount=D(100),
                    description="salary",
                    is_income=True,
                    currency=CurrencyEnum.USD,
                ),
            ),
            (
                "byn 25-5 food",
                ParsedMessage(
                    amount=D(20), description="food", currency=CurrencyEnum.BYN
                ),
            ),
        ),
        ids=(
            "lowercase_currency_prefix",
            "uppercase_currency_prefix",
            "currency_prefix_no_decimal",
            "currency_prefix_income",
            "currency_prefix_with_arithmetic",
        ),
    )
    async def test_message_parsing_with_currency_override(
        self, message_text: str, expected_result: ParsedMessage
    ):
        processed_result = ParsedMessage.from_message(message_text)
        assert processed_result == expected_result

    async def test_message_parsing_unknown_prefix_is_not_treated_as_currency(self):
        # 'abc' is not a supported currency code, so it stays part of the
        # (invalid) amount and parsing fails just like before this feature.
        with pytest.raises(Exception):
            ParsedMessage.from_message("abc 25 food")

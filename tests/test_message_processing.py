from decimal import Decimal as D

import pytest

from models.dto.parsed_message import ParsedMessage


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

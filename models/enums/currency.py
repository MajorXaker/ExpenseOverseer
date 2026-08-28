from enum import StrEnum


class CurrencyEnum(StrEnum):
    BYN = "BYN"
    USD = "USD"
    RUB = "RUB"
    EUR = "EUR"
    CNY = "CNY"
    BTC = "BTC"
    ETH = "ETH"
    PLN = "PLN"


# Currencies a user can pick as their default in /settings, or use as a
# per-transaction override prefix (e.g. "pln 12.5 taxi"). BYN stays the
# fallback default for new users / users who never picked one.
DEFAULT_CURRENCY = CurrencyEnum.BYN
SUPPORTED_CURRENCIES: tuple[CurrencyEnum, ...] = (
    CurrencyEnum.BYN,
    CurrencyEnum.USD,
    CurrencyEnum.EUR,
    CurrencyEnum.PLN,
)

from datetime import datetime


def get_month_window(months_ago: int = 0) -> tuple[datetime, datetime]:
    """
    Calculate month boundaries in pure Python.
    Returns (start_datetime, end_datetime) for the target month.

    Args:
        months_ago: 0 = current month, 1 = previous month, etc.

    Returns:
        Tuple of (month_start, month_end) as datetime objects
    """
    now = datetime.now()

    year = now.year
    month = now.month

    month -= months_ago
    while month <= 0:
        month += 12
        year -= 1

    month_start = datetime(year, month, 1, 0, 0, 0)

    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    month_end = datetime(next_year, next_month, 1, 0, 0, 0)

    return month_start, month_end


def days_in_month(year: int, month: int) -> int:
    """Return the number of days in a given month."""
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1
    return (datetime(next_year, next_month, 1) - datetime(year, month, 1)).days

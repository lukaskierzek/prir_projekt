import pandas as pd
from datetime import datetime

from domain.models import LogRecord


def filter_by_log_level(
        dataframe: pd.DataFrame,
        log_level: str,
) -> pd.DataFrame:
    """
    Filter logs by selected log level.

    Args:
        dataframe: Parsed logs DataFrame.
        log_level: e.g. ERROR, WARNING, INFO.

    Returns:
        Filtered DataFrame.
    """

    return dataframe[
        dataframe["Level"].str.upper() == log_level.upper()
        ]


def filter_by_date_range(
        dataframe: pd.DataFrame,
        start_date: str,
        end_date: str,
) -> pd.DataFrame:
    """
    Filter logs by date range.

    Args:
        dataframe: Parsed logs DataFrame.
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).

    Returns:
        Filtered DataFrame.
    """

    return dataframe[
        (dataframe["Date"] >= start_date)
        & (dataframe["Date"] <= end_date)
        ]


def filter_by_phrase(
        dataframe: pd.DataFrame,
        column: str,
        phrase: str,
) -> pd.DataFrame:
    """
    Filter rows containing selected phrase.

    Args:
        dataframe: Parsed logs DataFrame.
        column: Column to search.
        phrase: Phrase to search for.

    Returns:
        Filtered DataFrame.
    """

    return dataframe[
        dataframe[column].str.contains(
            phrase,
            case=False,
            na=False,
        )
    ]


def matches_level_filter(
    record: LogRecord,
    allowed_levels: tuple[str, ...],
) -> bool:
    if not allowed_levels:
        return True
    return record.level.upper() in allowed_levels


def matches_date_range(
    record: LogRecord,
    date_from: datetime | None,
    date_to: datetime | None,
) -> bool:
    if date_from is not None and record.timestamp < date_from:
        return False
    if date_to is not None and record.timestamp > date_to:
        return False
    return True

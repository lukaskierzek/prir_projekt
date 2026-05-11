import pandas as pd


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

import pandas as pd


def count_phrase_occurrences(
    dataframe: pd.DataFrame,
    column: str,
    phrase: str
):

    return dataframe[column].str.contains(
        phrase,
        case=False,
        na=False
    ).sum()


def count_log_levels(dataframe: pd.DataFrame) -> pd.Series:
    """
    Count occurrences of all log levels.
    """

    return dataframe["Level"].value_counts()
import pandas as pd


def prepare_datetime_column(
        dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create combined datetime column.
    """

    dataframe = dataframe.copy()

    dataframe["Datetime"] = pd.to_datetime(
        dataframe["Date"] + " " + dataframe["Time"],
        format="%Y-%m-%d %H:%M:%S,%f"
    )

    return dataframe


def count_logs_per_hour(
        dataframe: pd.DataFrame,
) -> pd.DataFrame | pd.Series:
    """
    Count logs grouped by hour.
    """

    dataframe = prepare_datetime_column(dataframe)

    return dataframe.groupby(
        dataframe["Datetime"].dt.hour
    ).size()


def count_errors_per_hour(
        dataframe: pd.DataFrame,
) -> pd.Series:
    """
    Count ERROR logs per hour.
    """

    dataframe = prepare_datetime_column(dataframe)

    errors = dataframe[
        dataframe["Level"].str.upper() == "ERROR"
        ]

    return errors.groupby(
        errors["Datetime"].dt.hour
    ).size()

from pathlib import Path
import re

import pandas as pd


LOG_PATTERN = re.compile(
    r"^(?P<Date>\d{4}-\d{2}-\d{2})\s+"
    r"(?P<Time>\d{2}:\d{2}:\d{2},\d{3})\s+"
    r"(?P<Level>\w+)\s+"
    r"\[(?P<Process>[^\]]+)\]\s+"
    r"(?P<Component>.*?):\s+"
    r"(?P<Content>.*)$"
)


def parse_line(line: str) -> dict | None:
    """
    Parse a single raw log line.

    Args:
        line: Raw log line.

    Returns:
        Dictionary with parsed fields or None if parsing failed.
    """

    match = LOG_PATTERN.match(line.strip())

    if not match:
        return None

    return match.groupdict()


def parse_log_file(file_path: str | Path) -> pd.DataFrame:
    """
    Parse an entire log file into a pandas DataFrame.

    Args:
        file_path: Path to raw .log file.

    Returns:
        DataFrame containing parsed logs.
    """

    parsed_logs = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            parsed_line = parse_line(line)

            if parsed_line:
                parsed_line["LineId"] = line_number
                parsed_logs.append(parsed_line)

    return pd.DataFrame(parsed_logs)


def save_dataframe_to_csv(
    dataframe: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """
    Save DataFrame to CSV file.

    Args:
        dataframe: DataFrame to save.
        output_path: Output CSV path.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    dataframe.to_csv(output_path, index=False)


def load_and_parse_logs(
    input_path: str | Path,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """
    Parse logs and optionally save them to CSV.

    Args:
        input_path: Path to raw log file.
        output_path: Optional CSV output path.

    Returns:
        Parsed logs as DataFrame.
    """

    dataframe = parse_log_file(input_path)

    if output_path:
        save_dataframe_to_csv(dataframe, output_path)

    return dataframe
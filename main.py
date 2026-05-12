import argparse
from datetime import datetime

from config import DATE_ONLY_INPUT_FORMAT, DATETIME_INPUT_FORMAT, DEFAULT_PHRASES
from domain.models import AnalysisConfig
from processing.analyzer import analyze_log_file
from report import print_report, save_filtered_lines_csv, save_report_json


def _parse_datetime(value: str | None, is_end: bool = False) -> datetime | None:
    if value is None:
        return None
    if len(value) == 10:
        suffix = " 23:59:59.999999" if is_end else " 00:00:00.000000"
        value = value + suffix
        return datetime.strptime(value, f"{DATE_ONLY_INPUT_FORMAT} %H:%M:%S.%f")
    return datetime.strptime(value, DATETIME_INPUT_FORMAT)


def main():
    parser = argparse.ArgumentParser(
        description="Log analysis for phrase counts, filtering and time stats."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to log file",
    )

    parser.add_argument(
        "--levels",
        nargs="*",
        default=[],
        help="Filter by levels, e.g. ERROR WARNING INFO",
    )

    parser.add_argument(
        "--phrases",
        nargs="*",
        default=list(DEFAULT_PHRASES),
        help="Phrases to count in message content",
    )

    parser.add_argument(
        "--from-date",
        type=str,
        help="Start datetime (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)",
    )

    parser.add_argument(
        "--to-date",
        type=str,
        help="End datetime (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        help="Optional path to save full report as JSON",
    )
    parser.add_argument(
        "--output-filtered-csv",
        type=str,
        help="Optional path to save filtered lines as CSV",
    )

    args = parser.parse_args()

    config = AnalysisConfig.from_iterables(
        phrases=args.phrases,
        levels=args.levels,
        date_from=_parse_datetime(args.from_date),
        date_to=_parse_datetime(args.to_date, is_end=True),
    )
    result = analyze_log_file(args.input, config)
    print_report(result)
    if args.output_json:
        save_report_json(result, args.output_json)
        print(f"Saved JSON report to: {args.output_json}")
    if args.output_filtered_csv:
        save_filtered_lines_csv(result, args.output_filtered_csv)
        print(f"Saved filtered lines CSV to: {args.output_filtered_csv}")


if __name__ == "__main__":
    main()

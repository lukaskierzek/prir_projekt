import argparse

from parser.log_parser import load_and_parse_logs
from processing.counters import (
    count_log_levels,
    count_phrase_occurrences,
)
from processing.filters import (
    filter_by_log_level,
    filter_by_date_range,
)


def main():
    parser = argparse.ArgumentParser(
        description="Log Analysis Application"
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Path to log file"
    )

    parser.add_argument(
        "--count-levels",
        action="store_true",
        help="Count all log levels"
    )

    parser.add_argument(
        "--filter-level",
        type=str,
        help="Filter logs by selected level"
    )

    parser.add_argument(
        "--phrase",
        type=str,
        help="Search phrase in log content"
    )

    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date YYYY-MM-DD"
    )

    parser.add_argument(
        "--end-date",
        type=str,
        help="End date YYYY-MM-DD"
    )

    args = parser.parse_args()

    dataframe = load_and_parse_logs(args.file)

    # Count log levels
    if args.count_levels:
        print("\n=== LOG LEVEL COUNTS ===\n")
        print(count_log_levels(dataframe))

    # Filter by level
    if args.filter_level:
        filtered = filter_by_log_level(
            dataframe,
            args.filter_level
        )

        print(f"\n=== {args.filter_level.upper()} LOGS ===\n")
        print(filtered.head())

        print(f"\nRows found: {len(filtered)}")

    # Count phrase occurrences
    if args.phrase:
        count = count_phrase_occurrences(
            dataframe,
            "Content",
            args.phrase
        )

        print(
            f'\nPhrase "{args.phrase}" found {count} times'
        )

    if args.start_date and args.end_date:
        filtered = filter_by_date_range(
            dataframe,
            args.start_date,
            args.end_date
        )

        print(
            f"\n=== LOGS FROM {args.start_date} TO {args.end_date} ===\n"
        )

        print(filtered.head())

        print(f"\nRows found: {len(filtered)}")


if __name__ == "__main__":
    main()

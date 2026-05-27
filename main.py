import argparse
from datetime import datetime

from config import DATE_ONLY_INPUT_FORMAT, DATETIME_INPUT_FORMAT
from domain.models import AnalysisConfig
from parallel.cuda.benchmark import benchmark_cuda
from parallel.mpi.runner import run_mpi_token_count
from parallel.openmp.benchmark import benchmark_openmp
from processing.analyzer import analyze_log_file
from processing.statistics import top_error_hours
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
        "--level",
        action="append",
        default=[],
        help="Single level filter, can be repeated (e.g. --level ERROR --level WARNING)",
    )

    parser.add_argument(
        "--phrases",
        nargs="*",
        default=[],
        help="Phrases to count in message content",
    )
    parser.add_argument(
        "--phrase",
        action="append",
        default=[],
        help="Single phrase to count, can be repeated",
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
        "--start-date",
        type=str,
        help="Alias for --from-date",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="Alias for --to-date",
    )
    parser.add_argument(
        "--filter-level",
        type=str,
        help="Single level filter alias (e.g. ERROR)",
    )
    parser.add_argument(
        "--show-errors-per-hour",
        action="store_true",
        help="Print per-hour counts for selected --error-type",
    )
    parser.add_argument(
        "--show-level-counts",
        action="store_true",
        help="Print level counts",
    )
    parser.add_argument(
        "--top-error-hours",
        type=int,
        default=0,
        help="Print only top N per-hour rows (0 = disabled)",
    )
    parser.add_argument(
        "--error-type",
        choices=["ERROR", "WARNING", "INFO", "FATAL"],
        default="ERROR",
        help="Event level used for per-hour time statistics",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of printed rows in selected outputs",
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
    parser.add_argument(
        "--parallel-mode",
        choices=["none", "openmp", "mpi", "cuda"],
        default="none",
        help="Run additional parallel token benchmark path",
    )
    parser.add_argument(
        "--openmp-workers",
        type=int,
        default=4,
        help="Workers for OpenMP-like Python benchmark path",
    )
    parser.add_argument(
        "--cuda-threads-per-block",
        type=int,
        default=256,
        help="Threads per CUDA block for CUDA benchmark path",
    )

    args = parser.parse_args()

    levels = list(args.levels)
    if args.level:
        levels.extend(args.level)
    if args.filter_level:
        levels.append(args.filter_level)

    phrases = list(args.phrases)
    if args.phrase:
        phrases.extend(args.phrase)

    from_date = args.start_date or args.from_date
    to_date = args.end_date or args.to_date

    config = AnalysisConfig.from_iterables(
        phrases=phrases,
        levels=levels,
        error_type=args.error_type,
        limit=args.limit,
        date_from=_parse_datetime(from_date),
        date_to=_parse_datetime(to_date, is_end=True),
    )
    result = analyze_log_file(args.input, config)
    print_report(result, limit=args.limit)

    if args.show_level_counts:
        print("\n=== LEVEL COUNTS (CLI VIEW) ===")
        items = list(result.level_counts.items())
        if args.limit:
            items = items[: args.limit]
        for level, count in items:
            print(f"{level}: {count}")

    if args.show_errors_per_hour:
        print(f"\n=== {args.error_type} PER HOUR (CLI VIEW) ===")
        hour_items = list(result.errors_per_hour.items())
        if args.top_error_hours > 0:
            hour_items = top_error_hours(result, top_n=args.top_error_hours)
        if args.limit:
            hour_items = hour_items[: args.limit]
        if not hour_items:
            print(f"No {args.error_type} events found.")
        else:
            for hour, count in hour_items:
                print(f"{hour} -> {count}")

    with open(args.input, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    if args.parallel_mode == "openmp":
        parallel_result = benchmark_openmp(lines, workers=args.openmp_workers)
        print("\n=== OPENMP-LIKE TOKENIZATION ===")
        for key, value in parallel_result.items():
            print(f"{key}: {value}")
    elif args.parallel_mode == "mpi":
        mpi_result = run_mpi_token_count(lines)
        if mpi_result["rank"] == 0:
            print("\n=== MPI TOKENIZATION ===")
            for key, value in mpi_result.items():
                print(f"{key}: {value}")
    elif args.parallel_mode == "cuda":
        cuda_result = benchmark_cuda(
            lines,
            threads_per_block=args.cuda_threads_per_block,
        )
        print("\n=== CUDA TOKENIZATION ===")
        for key, value in cuda_result.items():
            print(f"{key}: {value}")

    if args.output_json:
        save_report_json(result, args.output_json)
        print(f"Saved JSON report to: {args.output_json}")
    if args.output_filtered_csv:
        save_filtered_lines_csv(result, args.output_filtered_csv)
        print(f"Saved filtered lines CSV to: {args.output_filtered_csv}")


if __name__ == "__main__":
    main()

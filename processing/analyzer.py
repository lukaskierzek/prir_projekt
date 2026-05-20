from collections import Counter

from domain.models import AnalysisConfig, AnalysisResult, LogRecord
from parser.log_parser import parse_line_to_record
from processing.filters import matches_date_range, matches_level_filter


def analyze_log_file(file_path: str, config: AnalysisConfig) -> AnalysisResult:
    phrase_counts = Counter({phrase: 0 for phrase in config.phrases})
    level_counts = Counter()
    errors_per_hour = Counter()
    filtered_lines: list[str] = []
    parse_errors = 0
    total_lines = 0
    parsed_lines = 0

    with open(file_path, "r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            total_lines += 1
            record = parse_line_to_record(raw_line, line_number)
            if record is None:
                parse_errors += 1
                continue

            parsed_lines += 1
            level_counts[record.level.upper()] += 1
            _update_phrase_counts(record, phrase_counts, config.phrases)
            _update_error_hour_stats(record, errors_per_hour, config.error_type)

            if (
                _matches_phrase_filter(record, config.phrases)
                and matches_level_filter(record, config.levels)
                and matches_date_range(record, config.date_from, config.date_to)
            ):
                filtered_lines.append(record.raw_line.rstrip("\n"))

    return AnalysisResult(
        phrase_counts=dict(phrase_counts),
        level_counts=dict(sorted(level_counts.items())),
        filtered_lines=filtered_lines,
        errors_per_hour=dict(sorted(errors_per_hour.items())),
        parse_errors=parse_errors,
        total_lines=total_lines,
        parsed_lines=parsed_lines,
    )


def _update_phrase_counts(
    record: LogRecord, phrase_counts: Counter, phrases: tuple[str, ...]
) -> None:
    message_upper = record.message.upper()
    for phrase in phrases:
        if phrase.upper() in message_upper:
            phrase_counts[phrase] += 1


def _update_error_hour_stats(
    record: LogRecord, errors_per_hour: Counter, error_type: str
) -> None:
    if record.level.upper() != error_type.upper():
        return
    hour_bucket = record.timestamp.strftime("%Y-%m-%d %H:00")
    errors_per_hour[hour_bucket] += 1


def _matches_phrase_filter(record: LogRecord, phrases: tuple[str, ...]) -> bool:
    if not phrases:
        return True
    message_upper = record.message.upper()
    return any(phrase.upper() in message_upper for phrase in phrases)

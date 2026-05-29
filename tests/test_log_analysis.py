from datetime import datetime
from pathlib import Path

from domain.models import AnalysisConfig
from parallel.cuda.benchmark import benchmark_cuda
from parser.log_parser import parse_line_to_record
from processing.analyzer import analyze_log_file
from processing.filters import matches_date_range, matches_level_filter
from processing.top_words import top_words


def test_parse_line_to_record_success() -> None:
    line = "2026-05-12 11:22:33,123 ERROR [proc-1] AuthService: Login failed\n"
    record = parse_line_to_record(line, 7)
    assert record is not None
    assert record.level == "ERROR"
    assert record.component == "AuthService"
    assert record.line_id == 7


def test_parse_line_to_record_invalid() -> None:
    assert parse_line_to_record("invalid line\n", 1) is None


def test_filters() -> None:
    line = "2026-05-12 11:22:33,123 WARNING [p] Cmp: Something happened\n"
    record = parse_line_to_record(line, 1)
    assert record is not None
    assert matches_level_filter(record, ("WARNING",))
    assert not matches_level_filter(record, ("ERROR",))
    assert matches_date_range(record, datetime(2026, 5, 12, 0, 0, 0), None)
    assert not matches_date_range(record, datetime(2026, 5, 13, 0, 0, 0), None)


def test_analyze_log_file(tmp_path: Path) -> None:
    log_path = tmp_path / "sample.log"
    log_path.write_text(
        "2026-05-12 10:00:00,000 INFO [p1] App: Startup complete\n"
        "2026-05-12 10:15:00,000 ERROR [p2] App: ERROR while processing\n"
        "2026-05-12 10:45:00,000 WARNING [p3] App: Warning observed\n"
        "bad line\n",
        encoding="utf-8",
    )
    config = AnalysisConfig.from_iterables(
        phrases=("ERROR", "WARNING", "INFO"),
        levels=("ERROR", "WARNING"),
    )
    result = analyze_log_file(str(log_path), config)
    assert result.total_lines == 4
    assert result.parsed_lines == 3
    assert result.parse_errors == 1
    assert result.phrase_counts["ERROR"] == 1
    assert result.phrase_counts["WARNING"] == 1
    assert result.phrase_counts["INFO"] == 0
    assert result.level_counts == {"ERROR": 1, "INFO": 1, "WARNING": 1}
    assert len(result.filtered_lines) == 2
    assert result.errors_per_hour == {"2026-05-12 10:00": 1}


def test_cuda_benchmark_schema() -> None:
    result = benchmark_cuda(["alpha beta\n", "gamma\n"], threads_per_block=64)
    assert result["tokens"] == 3
    assert result["bytes"] == len("alpha beta\ngamma\n".encode("utf-8"))
    assert "throughput_gb_s" in result
    assert "mode" in result


def test_top_words() -> None:
    assert top_words(["ERROR info ERROR\n", "warning info\n"], top_n=2) == [
        ("ERROR", 2),
        ("INFO", 2),
    ]

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable


@dataclass(frozen=True)
class LogRecord:
    timestamp: datetime
    level: str
    process: str
    component: str
    message: str
    raw_line: str
    line_id: int


@dataclass(frozen=True)
class AnalysisConfig:
    phrases: tuple[str, ...] = ("ERROR", "WARNING", "INFO")
    levels: tuple[str, ...] = ()
    date_from: datetime | None = None
    date_to: datetime | None = None

    @staticmethod
    def from_iterables(
        phrases: Iterable[str] | None = None,
        levels: Iterable[str] | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> "AnalysisConfig":
        return AnalysisConfig(
            phrases=tuple(phrases or ("ERROR", "WARNING", "INFO")),
            levels=tuple(level.upper() for level in (levels or ())),
            date_from=date_from,
            date_to=date_to,
        )


@dataclass
class AnalysisResult:
    phrase_counts: dict[str, int] = field(default_factory=dict)
    level_counts: dict[str, int] = field(default_factory=dict)
    filtered_lines: list[str] = field(default_factory=list)
    errors_per_hour: dict[str, int] = field(default_factory=dict)
    parse_errors: int = 0
    total_lines: int = 0
    parsed_lines: int = 0

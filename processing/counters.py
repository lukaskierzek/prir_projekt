from collections import Counter
from typing import Iterable

from domain.models import AnalysisResult


def count_phrase_occurrences_in_text(
    lines: Iterable[str],
    phrase: str,
) -> int:
    phrase_upper = phrase.upper()
    return sum(1 for line in lines if phrase_upper in line.upper())


def count_levels_from_filtered_lines(lines: Iterable[str]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for line in lines:
        line_upper = line.upper()
        if " ERROR " in line_upper:
            counter["ERROR"] += 1
        elif " WARNING " in line_upper:
            counter["WARNING"] += 1
        elif " INFO " in line_upper:
            counter["INFO"] += 1
    return dict(counter)


def phrase_counts(result: AnalysisResult) -> dict[str, int]:
    return dict(result.phrase_counts)

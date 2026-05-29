from domain.models import AnalysisResult


def total_parsed_ratio(result: AnalysisResult) -> float:
    if result.total_lines == 0:
        return 0.0
    return result.parsed_lines / result.total_lines


def total_matched_ratio(result: AnalysisResult) -> float:
    if result.parsed_lines == 0:
        return 0.0
    return len(result.filtered_lines) / result.parsed_lines



def top_error_hours(
    result: AnalysisResult,
    top_n: int = 5,
) -> list[tuple[str, int]]:
    items = sorted(
        result.errors_per_hour.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    return items[:top_n]

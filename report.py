from domain.models import AnalysisResult
import json
from pathlib import Path

import pandas as pd


def print_report(result: AnalysisResult) -> None:
    print("\n=== SUMMARY ===")
    print(f"Total lines: {result.total_lines}")
    print(f"Parsed lines: {result.parsed_lines}")
    print(f"Parse errors: {result.parse_errors}")

    print("\n=== PHRASE COUNTS ===")
    for phrase, count in result.phrase_counts.items():
        print(f"{phrase}: {count}")
    print("\n=== LEVEL COUNTS (ALL DETECTED) ===")
    for level, count in result.level_counts.items():
        print(f"{level}: {count}")

    print("\n=== ERRORS PER HOUR ===")
    if not result.errors_per_hour:
        print("No ERROR events found.")
    else:
        for hour, count in result.errors_per_hour.items():
            print(f"{hour} -> {count}")

    print("\n=== FILTERED LINES (first 10) ===")
    for line in result.filtered_lines[:10]:
        print(line)
    print(f"Matched lines: {len(result.filtered_lines)}")


def result_to_dict(result: AnalysisResult) -> dict:
    return {
        "summary": {
            "total_lines": result.total_lines,
            "parsed_lines": result.parsed_lines,
            "parse_errors": result.parse_errors,
            "matched_lines": len(result.filtered_lines),
        },
        "phrase_counts": result.phrase_counts,
        "level_counts": result.level_counts,
        "errors_per_hour": result.errors_per_hour,
        "filtered_lines": result.filtered_lines,
    }


def save_report_json(result: AnalysisResult, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(result_to_dict(result), handle, ensure_ascii=False, indent=2)


def save_filtered_lines_csv(result: AnalysisResult, output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe = pd.DataFrame({"line": result.filtered_lines})
    dataframe.to_csv(path, index=False)

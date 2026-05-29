import argparse
import time
from pathlib import Path

from visualization.matplotlib_setup import configure_matplotlib

configure_matplotlib()

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from config import DEFAULT_INPUT_LOG
from domain.models import AnalysisConfig
from processing.analyzer import analyze_log_file


def read_lines_time(input_path: str) -> float:
    start = time.perf_counter()
    with open(input_path, "r", encoding="utf-8") as handle:
        handle.readlines()
    return time.perf_counter() - start


def plot_level_counts(level_counts: dict[str, int], save_path: Path) -> None:
    items = sorted(level_counts.items(), key=lambda item: item[1], reverse=True)
    labels = [level for level, _ in items]
    values = [count for _, count in items]

    plt.figure(figsize=(8, 4))
    bars = plt.bar(labels, values, color="#3568a8")
    plt.title("Log events by level")
    plt.xlabel("Level")
    plt.ylabel("Count")
    plt.grid(axis="y", alpha=0.3)
    plt.bar_label(bars, fmt="%.0f", padding=3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_top_error_hours(errors_per_hour: dict[str, int], save_path: Path) -> None:
    items = sorted(errors_per_hour.items(), key=lambda item: item[1], reverse=True)[:30]
    items = sorted(items, key=lambda item: item[0])
    hours = [hour for hour, _ in items]
    counts = [count for _, count in items]

    plt.figure(figsize=(12, 4.8))
    plt.bar(hours, counts, color="#c43b3b")
    plt.title("Top ERROR-heavy hours")
    plt.xlabel("Hour")
    plt.ylabel("ERROR count")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_io_vs_compute(
    io_time: float,
    reports_dir: Path,
    save_path: Path,
) -> None:
    rows = [("File read", io_time)]

    openmp_csv = reports_dir / "benchmark_openmp.csv"
    if openmp_csv.exists():
        openmp_df = pd.read_csv(openmp_csv)
        rows.append(("Best OpenMP", float(openmp_df["time"].min())))

    mpi_csv = reports_dir / "benchmark_mpi.csv"
    if mpi_csv.exists():
        mpi_df = pd.read_csv(mpi_csv)
        rows.append(("Best MPI", float(mpi_df["time"].min())))

    cuda_csv = reports_dir / "benchmark_cuda.csv"
    if cuda_csv.exists():
        cuda_df = pd.read_csv(cuda_csv)
        rows.append(("Best CUDA", float(cuda_df["time"].min())))

    labels = [label for label, _ in rows]
    values = [value for _, value in rows]

    plt.figure(figsize=(9, 4))
    bars = plt.bar(labels, values, color=["#777777", "#3568a8", "#3f8f46", "#c43b3b"])
    plt.title("I/O time vs compute time")
    plt.xlabel("Operation")
    plt.ylabel("Time [s]")
    plt.grid(axis="y", alpha=0.3)
    plt.bar_label(bars, fmt="%.3f", padding=3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_openmp_mpi_speedup(reports_dir: Path, save_path: Path) -> None:
    openmp_csv = reports_dir / "benchmark_openmp.csv"
    mpi_csv = reports_dir / "benchmark_mpi.csv"
    if not openmp_csv.exists() or not mpi_csv.exists():
        return

    openmp_df = pd.read_csv(openmp_csv).sort_values("threads")
    mpi_df = pd.read_csv(mpi_csv).sort_values("processes")

    plt.figure(figsize=(8, 4.5))
    plt.plot(
        openmp_df["threads"],
        openmp_df["speedup"],
        marker="o",
        linewidth=2,
        label="OpenMP-like",
    )
    plt.plot(
        mpi_df["processes"],
        mpi_df["speedup"],
        marker="o",
        linewidth=2,
        label="MPI",
    )
    max_unit = int(max(openmp_df["threads"].max(), mpi_df["processes"].max()))
    plt.plot(range(1, max_unit + 1), range(1, max_unit + 1), "--", label="Ideal")
    plt.title("OpenMP-like vs MPI speedup")
    plt.xlabel("Workers / processes")
    plt.ylabel("Speedup")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_LOG))
    parser.add_argument("--save-dir", default="reports")
    args = parser.parse_args()

    reports_dir = Path(args.save_dir)
    plots_dir = reports_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    result = analyze_log_file(args.input, AnalysisConfig())
    io_time = read_lines_time(args.input)

    plot_level_counts(result.level_counts, plots_dir / "level_counts.png")
    plot_top_error_hours(result.errors_per_hour, plots_dir / "top_error_hours.png")
    plot_io_vs_compute(io_time, reports_dir, plots_dir / "io_vs_compute_time.png")
    plot_openmp_mpi_speedup(reports_dir, plots_dir / "openmp_mpi_speedup.png")

    print(f"Saved extra plots to: {plots_dir}")


if __name__ == "__main__":
    main()

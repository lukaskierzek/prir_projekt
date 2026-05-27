try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    plt = None
from datetime import datetime
from pathlib import Path


def print_dataframe(
    dataframe,
    rows: int = 10,
):
    print(dataframe.head(rows).to_string(index=False))


def plot_series(
    series,
    title: str,
    xlabel: str,
    ylabel: str,
    save_path: str | None = None,
):
    series.plot(kind="bar")

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
        return
    plt.show()


def plot_errors_per_hour(
    errors_per_hour: dict[str, int],
    title: str = "Errors Per Hour",
    hour_from: str | None = None,
    hour_to: str | None = None,
    max_points: int | None = None,
    save_path: str | None = None,
) -> None:
    if not errors_per_hour:
        print("plot_errors_per_hour: no data to plot (empty errors_per_hour).")
        return

    items = sorted(errors_per_hour.items(), key=lambda x: x[0])

    def parse_hour(value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d %H:00")

    try:
        if hour_from:
            dt_from = parse_hour(hour_from)
            items = [(h, c) for h, c in items if parse_hour(h) >= dt_from]
        if hour_to:
            dt_to = parse_hour(hour_to)
            items = [(h, c) for h, c in items if parse_hour(h) <= dt_to]
    except ValueError as exc:
        raise ValueError(
            "hour_from/hour_to must use format 'YYYY-MM-DD HH:00'"
        ) from exc
    if max_points is not None and max_points > 0:
        items = items[:max_points]
    if not items:
        first_hour = min(errors_per_hour.keys())
        last_hour = max(errors_per_hour.keys())
        print(
            "plot_errors_per_hour: no points after filtering. "
            f"Available range: {first_hour} .. {last_hour}"
        )
        return

    hours = [h for h, _ in items]
    counts = [c for _, c in items]
    plt.figure(figsize=(10, 4))
    plt.bar(hours, counts)
    plt.title(title)
    plt.xlabel("Hour")
    plt.ylabel("Errors")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
        return
    plt.show()


def plot_speedup_efficiency(
    units: list[int],
    speedup: list[float],
    efficiency: list[float],
    label: str,
    units_label: str,
    save_path: str,
) -> None:
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(units, speedup, marker="o", label=label)
    ax[0].plot(units, units, linestyle="--", label="Ideal")
    ax[0].set_xlabel(units_label)
    ax[0].set_ylabel("Przyspieszenie")
    ax[0].set_title(f"{label} Speedup")
    ax[0].grid(True)
    ax[0].legend()

    ax[1].plot(units, efficiency, marker="o", label=label)
    ax[1].axhline(1.0, linestyle="--")
    ax[1].set_xlabel(units_label)
    ax[1].set_ylabel("Efektywność")
    ax[1].set_title(f"{label} Efficiency")
    ax[1].grid(True)
    ax[1].legend()

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_parallel_comparison(
    openmp_rows: list[dict[str, float]],
    mpi_rows: list[dict[str, float]],
    cuda_rows: list[dict[str, float]] | None = None,
    save_path: str | None = None,
) -> dict[str, float]:
    openmp_rows = sorted(openmp_rows, key=lambda r: r["units"])
    mpi_rows = sorted(mpi_rows, key=lambda r: r["units"])
    cuda_rows = sorted(cuda_rows or [], key=lambda r: r["units"])

    seq_candidates = [r["time"] for r in openmp_rows if r["units"] == 1] + [
        r["time"] for r in mpi_rows if r["units"] == 1
    ]
    if not seq_candidates:
        raise RuntimeError(
            "Brak pomiaru sekwencyjnego (1). Uruchom benchmarki dla 1 worker/process."
        )
    seq_time = min(seq_candidates)

    openmp_speedup = [(r["units"], seq_time / r["time"]) for r in openmp_rows]
    mpi_speedup = [(r["units"], seq_time / r["time"]) for r in mpi_rows]
    cuda_speedup = [
        (r["units"], seq_time / r["time"]) for r in cuda_rows if r["time"] > 0
    ]

    fig, ax = plt.subplots(1, 2, figsize=(13, 4))
    ax[0].plot([1], [seq_time], marker="o", label="Sequential (baseline)")
    ax[0].plot(
        [r["units"] for r in openmp_rows],
        [r["time"] for r in openmp_rows],
        marker="o",
        label="OpenMP-like",
    )
    ax[0].plot(
        [r["units"] for r in mpi_rows],
        [r["time"] for r in mpi_rows],
        marker="o",
        label="MPI",
    )
    if cuda_rows:
        ax[0].plot(
            [r["units"] for r in cuda_rows],
            [r["time"] for r in cuda_rows],
            marker="o",
            label="CUDA",
        )
    units_label = "Workers / Processes / CUDA threads per block" if cuda_rows else "Workers / Processes"
    ax[0].set_xlabel(units_label)
    ax[0].set_ylabel("Time [s]")
    ax[0].set_title("Execution Time Comparison")
    ax[0].grid(True)
    ax[0].legend()
    if cuda_rows:
        all_units = sorted(
            {
                *[r["units"] for r in openmp_rows],
                *[r["units"] for r in mpi_rows],
                *[r["units"] for r in cuda_rows],
            }
        )
        ax[0].set_xscale("log", base=2)
        ax[0].set_yscale("log")
        ax[0].set_xticks(all_units)
        ax[0].set_xticklabels([str(unit) for unit in all_units])

    ax[1].plot(
        [u for u, _ in openmp_speedup],
        [s for _, s in openmp_speedup],
        marker="o",
        label="OpenMP-like",
    )
    ax[1].plot(
        [u for u, _ in mpi_speedup],
        [s for _, s in mpi_speedup],
        marker="o",
        label="MPI",
    )
    if cuda_speedup:
        ax[1].plot(
            [u for u, _ in cuda_speedup],
            [s for _, s in cuda_speedup],
            marker="o",
            label="CUDA",
        )
    max_units = max([u for u, _ in openmp_speedup] + [u for u, _ in mpi_speedup])
    ax[1].plot(
        list(range(1, max_units + 1)),
        list(range(1, max_units + 1)),
        linestyle="--",
        label="Ideal",
    )
    ax[1].set_xlabel(units_label)
    ax[1].set_ylabel("Speedup vs sequential")
    ax[1].set_title("Speedup Comparison")
    ax[1].grid(True)
    ax[1].legend()
    if cuda_speedup:
        all_units = sorted(
            {
                *[u for u, _ in openmp_speedup],
                *[u for u, _ in mpi_speedup],
                *[u for u, _ in cuda_speedup],
            }
        )
        ax[1].set_xscale("log", base=2)
        ax[1].set_yscale("log")
        ax[1].set_xticks(all_units)
        ax[1].set_xticklabels([str(unit) for unit in all_units])

    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150)
        plt.close()
    else:
        plt.show()

    summary = {
        "sequential_time_s": round(seq_time, 6),
        "best_openmp_time_s": round(min(r["time"] for r in openmp_rows), 6),
        "best_mpi_time_s": round(min(r["time"] for r in mpi_rows), 6),
    }
    if cuda_rows:
        summary["best_cuda_time_s"] = round(min(r["time"] for r in cuda_rows), 6)
    return summary


def plot_level_counts(
    level_counts: dict[str, int],
    title: str = "Liczba logów per level",
    save_path: str | None = None,
) -> None:
    if not level_counts:
        print("plot_level_counts: no data to plot (empty level_counts).")
        return

    items = sorted(level_counts.items(), key=lambda x: x[1], reverse=True)
    levels = [k for k, _ in items]
    counts = [v for _, v in items]

    plt.figure(figsize=(10, 4))
    plt.bar(levels, counts)
    plt.title(title)
    plt.xlabel("Level")
    plt.ylabel("Count")
    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150)
        plt.close()
        return
    plt.show()


def plot_level_filter_comparison(
    level_compare: dict[str, int],
    title: str = "Dopasowania dla filtru --level",
    save_path: str | None = None,
) -> None:
    if not level_compare:
        print("plot_level_filter_comparison: no data to plot (empty level_compare).")
        return

    items = list(level_compare.items())
    levels = [k for k, _ in items]
    counts = [v for _, v in items]

    plt.figure(figsize=(8, 4))
    plt.bar(levels, counts)
    plt.title(title)
    plt.xlabel("Level")
    plt.ylabel("Matched lines")
    plt.tight_layout()
    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150)
        plt.close()
        return
    plt.show()


def plot_top_words(
    words: list[tuple[str, int]],
    save_path: str,
    title: str = "Top-N words",
) -> None:
    if plt is None:
        print("plot_top_words: matplotlib is not installed; skipping plot.")
        return
    if not words:
        print("plot_top_words: no words to plot.")
        return

    labels = [word for word, _ in reversed(words)]
    counts = [count for _, count in reversed(words)]

    plt.figure(figsize=(10, 6))
    plt.barh(labels, counts)
    plt.title(title)
    plt.xlabel("Count")
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_cpu_gpu_comparison(
    rows: list[dict[str, float | str]],
    save_path: str,
) -> None:
    if plt is None:
        print("plot_cpu_gpu_comparison: matplotlib is not installed; skipping plot.")
        return
    if not rows:
        print("plot_cpu_gpu_comparison: no benchmark rows to plot.")
        return

    labels = [str(row["technology"]) for row in rows]
    throughput = [float(row["throughput_gb_s"]) for row in rows]

    plt.figure(figsize=(8, 4))
    plt.bar(labels, throughput)
    plt.ylabel("Throughput [GB/s]")
    plt.title("CPU/GPU throughput comparison")
    plt.grid(axis="y")
    plt.tight_layout()
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150)
    plt.close()

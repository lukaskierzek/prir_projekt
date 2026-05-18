import argparse
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from config import DEFAULT_INPUT_LOG
from parallel.openmp.benchmark import benchmark_openmp


def mpi_time(processes: int, input_path: str) -> float:
    cmd = [
        "mpiexec",
        "-n",
        str(processes),
        sys.executable,
        "main.py",
        "--input",
        input_path,
        "--parallel-mode",
        "mpi",
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
    for line in completed.stdout.splitlines():
        if line.strip().startswith("time:"):
            return float(line.split(":", 1)[1].strip())
    raise ValueError("Could not parse MPI time.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_LOG))
    parser.add_argument("--openmp-threads", nargs="+", type=int, default=[1, 2, 4, 8])
    parser.add_argument("--mpi-procs", nargs="+", type=int, default=[1, 2, 4, 8])
    parser.add_argument("--save-dir", default="reports")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    openmp_times = [benchmark_openmp(lines, workers=t)["time"] for t in args.openmp_threads]
    mpi_times = [mpi_time(p, args.input) for p in args.mpi_procs]

    rows = [
        {"technology": "OpenMP-like", "best_time": float(min(openmp_times))},
        {"technology": "MPI", "best_time": float(min(mpi_times))},
    ]

    df = pd.DataFrame(rows).sort_values("best_time")
    print(df)
    out_dir = Path(args.save_dir)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "benchmark_best_comparison.csv", index=False)

    plt.figure(figsize=(7, 4))
    plt.bar(df["technology"], df["best_time"])
    plt.ylabel("Czas [s] (mniej = lepiej)")
    plt.title("Porównanie najlepszych wyników (OpenMP-like vs MPI)")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig(plots_dir / "best_comparison_openmp_mpi.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()

import argparse
import subprocess
import sys
from pathlib import Path

from visualization.matplotlib_setup import configure_matplotlib

configure_matplotlib()

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from config import DEFAULT_INPUT_LOG
from parallel.cuda.benchmark import benchmark_cuda
from parallel.mpi.launcher import find_mpiexec
from parallel.openmp.benchmark import benchmark_openmp


def mpi_time(processes: int, input_path: str) -> float:
    mpiexec = find_mpiexec()
    if mpiexec is None:
        if processes != 1:
            raise RuntimeError(
                "mpiexec is not available; only 1-process fallback can run."
            )
        cmd = [
            sys.executable,
            "main.py",
            "--input",
            input_path,
            "--parallel-mode",
            "mpi",
        ]
    else:
        cmd = [
            mpiexec,
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
    parser.add_argument("--cuda-threads-per-block", nargs="+", type=int, default=[64, 128, 256, 512])
    parser.add_argument("--save-dir", default="reports")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    openmp_times = [
        benchmark_openmp(lines, workers=threads)["time"]
        for threads in args.openmp_threads
    ]
    mpi_procs = args.mpi_procs
    if find_mpiexec() is None:
        print("mpiexec not found; running MPI single-process fallback only.")
        mpi_procs = [1]

    mpi_times = [mpi_time(processes, args.input) for processes in mpi_procs]
    cuda_results = [
        benchmark_cuda(lines, threads_per_block=threads)
        for threads in args.cuda_threads_per_block
    ]
    cuda_times = [
        float(result["time"])
        for result in cuda_results
        if result["mode"] == "cuda"
    ]

    rows = [
        {"technology": "OpenMP-like", "best_time": float(min(openmp_times))},
        {"technology": "MPI", "best_time": float(min(mpi_times))},
    ]
    if cuda_times:
        rows.append({"technology": "CUDA", "best_time": float(min(cuda_times))})
    else:
        fallback_modes = ", ".join(sorted({str(result["mode"]) for result in cuda_results}))
        print(f"CUDA skipped in best comparison; modes observed: {fallback_modes}")

    df = pd.DataFrame(rows).sort_values("best_time")
    print(df)
    out_dir = Path(args.save_dir)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "benchmark_best_comparison.csv", index=False)

    plt.figure(figsize=(7, 4))
    plt.bar(df["technology"], df["best_time"])
    plt.ylabel("Time [s] (lower is better)")
    plt.title("Best benchmark comparison")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig(plots_dir / "best_comparison_openmp_mpi_cuda.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    main()

import argparse
import subprocess
import sys
from pathlib import Path

from visualization.matplotlib_setup import configure_matplotlib

configure_matplotlib()

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from config import DEFAULT_INPUT_LOG
from parallel.mpi.launcher import find_mpiexec


def parse_time(output: str) -> float:
    for line in output.splitlines():
        if line.strip().startswith("time:"):
            return float(line.split(":", 1)[1].strip())
    raise ValueError("Could not parse MPI time from output.")


def run_case(processes: int, input_path: str) -> float:
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
    return parse_time(completed.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_LOG))
    parser.add_argument("--procs", nargs="+", type=int, default=[1, 2, 4, 8])
    parser.add_argument("--save-dir", default="reports")
    args = parser.parse_args()

    if find_mpiexec() is None:
        print("mpiexec not found; running MPI single-process fallback only.")
        args.procs = [1]

    rows = []
    for p in args.procs:
        t = run_case(p, args.input)
        rows.append({"processes": p, "time": t})

    df = pd.DataFrame(rows).sort_values("processes")
    t1 = float(df.loc[df["processes"] == 1, "time"].iloc[0])
    df["speedup"] = t1 / df["time"]
    df["efficiency"] = df["speedup"] / df["processes"]
    print(df)
    out_dir = Path(args.save_dir)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "benchmark_mpi.csv", index=False)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(df["processes"], df["speedup"], marker="o", label="MPI")
    ax[0].plot(df["processes"], df["processes"], linestyle="--", label="Ideal")
    ax[0].set_xlabel("Processes")
    ax[0].set_ylabel("Speedup")
    ax[0].set_title("MPI Speedup")
    ax[0].grid(True)
    ax[0].legend()

    ax[1].plot(df["processes"], df["efficiency"], marker="o", label="MPI")
    ax[1].axhline(1.0, linestyle="--")
    ax[1].set_xlabel("Processes")
    ax[1].set_ylabel("Efficiency")
    ax[1].set_title("MPI Efficiency")
    ax[1].grid(True)
    ax[1].legend()

    plt.tight_layout()
    plt.savefig(plots_dir / "mpi_speedup_efficiency.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    main()

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from config import DEFAULT_INPUT_LOG
from parallel.cuda.benchmark import benchmark_cuda


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_LOG))
    parser.add_argument("--threads-per-block", nargs="+", type=int, default=[64, 128, 256, 512])
    parser.add_argument("--save-dir", default="reports")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    rows = []
    for threads in args.threads_per_block:
        result = benchmark_cuda(lines, threads_per_block=threads)
        rows.append(
            {
                "threads_per_block": threads,
                "time": float(result["time"]),
                "tokens": int(result["tokens"]),
                "bytes": int(result["bytes"]),
                "throughput_gb_s": float(result["throughput_gb_s"]),
                "mode": str(result["mode"]),
            }
        )

    df = pd.DataFrame(rows).sort_values("threads_per_block")
    baseline = float(df["time"].iloc[0])
    df["speedup"] = baseline / df["time"] if baseline > 0 else 0.0
    df["efficiency"] = df["speedup"] / df["threads_per_block"]

    print(df)
    out_dir = Path(args.save_dir)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "benchmark_cuda.csv", index=False)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(df["threads_per_block"], df["time"], marker="o", label="CUDA")
    ax[0].set_xlabel("Threads per block")
    ax[0].set_ylabel("Time [s]")
    ax[0].set_title("CUDA Execution Time")
    ax[0].grid(True)
    ax[0].legend()

    ax[1].plot(df["threads_per_block"], df["throughput_gb_s"], marker="o", label="CUDA")
    ax[1].set_xlabel("Threads per block")
    ax[1].set_ylabel("Throughput [GB/s]")
    ax[1].set_title("CUDA Throughput")
    ax[1].grid(True)
    ax[1].legend()

    plt.tight_layout()
    plt.savefig(plots_dir / "cuda_speedup_efficiency.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()

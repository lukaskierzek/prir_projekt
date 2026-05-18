import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from config import DEFAULT_INPUT_LOG
from parallel.openmp.benchmark import benchmark_openmp


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_LOG))
    parser.add_argument("--threads", nargs="+", type=int, default=[1, 2, 4, 8])
    parser.add_argument("--save-dir", default="reports")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    rows = []
    for t in args.threads:
        result = benchmark_openmp(lines, workers=t)
        rows.append({"threads": t, "time": float(result["time"])})

    df = pd.DataFrame(rows).sort_values("threads")
    t1 = float(df.loc[df["threads"] == 1, "time"].iloc[0])
    df["speedup"] = t1 / df["time"]
    df["efficiency"] = df["speedup"] / df["threads"]
    print(df)
    out_dir = Path(args.save_dir)
    plots_dir = out_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "benchmark_openmp.csv", index=False)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(df["threads"], df["speedup"], marker="o", label="OpenMP-like")
    ax[0].plot(df["threads"], df["threads"], linestyle="--", label="Ideal")
    ax[0].set_xlabel("Liczba wątków")
    ax[0].set_ylabel("Przyspieszenie")
    ax[0].set_title("OpenMP-like Speedup")
    ax[0].grid(True)
    ax[0].legend()

    ax[1].plot(df["threads"], df["efficiency"], marker="o", label="OpenMP-like")
    ax[1].axhline(1.0, linestyle="--")
    ax[1].set_xlabel("Liczba wątków")
    ax[1].set_ylabel("Efektywność")
    ax[1].set_title("OpenMP-like Efficiency")
    ax[1].grid(True)
    ax[1].legend()

    plt.tight_layout()
    plt.savefig(plots_dir / "openmp_speedup_efficiency.png", dpi=150)
    plt.show()


if __name__ == "__main__":
    main()

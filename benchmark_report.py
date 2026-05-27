import argparse
import time
from pathlib import Path

import pandas as pd

from config import DEFAULT_INPUT_LOG
from parallel.cuda.benchmark import benchmark_cuda
from parallel.openmp.benchmark import benchmark_openmp
from processing.top_words import top_words
from visualization.plots import plot_cpu_gpu_comparison, plot_top_words


def read_lines_with_timing(input_path: str) -> tuple[list[str], float, int]:
    start = time.perf_counter()
    with open(input_path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()
    elapsed = time.perf_counter() - start
    total_bytes = len("".join(lines).encode("utf-8", errors="ignore"))
    return lines, elapsed, total_bytes


def io_conclusion(io_time: float, compute_time: float) -> str:
    if compute_time <= 0:
        return "Brak wiarygodnego czasu obliczen do porownania z I/O."
    ratio = io_time / compute_time
    if ratio >= 1.0:
        return "I/O jest glownym waskim gardlem: odczyt pliku trwa dluzej niz obliczenia."
    if ratio >= 0.25:
        return "I/O ma istotny udzial w czasie wykonania i moze ograniczac skalowanie."
    return "I/O nie dominuje w tym pomiarze; wiekszy koszt jest po stronie obliczen."


def write_markdown_report(
    output_path: Path,
    rows: list[dict[str, float | int | str]],
    top_rows: list[tuple[str, int]],
    io_time: float,
    total_bytes: int,
) -> None:
    best_compute = min(float(row["time"]) for row in rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write("# Benchmark report\n\n")
        handle.write(f"- Input bytes: {total_bytes}\n")
        handle.write(f"- Input size GB: {total_bytes / 1_000_000_000:.6f}\n")
        handle.write(f"- File read time s: {io_time:.6f}\n")
        handle.write(f"- File read throughput GB/s: {total_bytes / io_time / 1_000_000_000:.6f}\n\n")

        handle.write("## CPU/GPU comparison\n\n")
        handle.write("| Technology | Mode | Time s | Throughput GB/s | Tokens |\n")
        handle.write("|---|---:|---:|---:|---:|\n")
        for row in rows:
            handle.write(
                f"| {row['technology']} | {row['mode']} | {float(row['time']):.6f} "
                f"| {float(row['throughput_gb_s']):.6f} | {int(row['tokens'])} |\n"
            )

        handle.write("\n## Top words\n\n")
        handle.write("| Word | Count |\n")
        handle.write("|---|---:|\n")
        for word, count in top_rows:
            handle.write(f"| {word} | {count} |\n")

        handle.write("\n## I/O bottleneck conclusion\n\n")
        handle.write(io_conclusion(io_time, best_compute))
        handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_LOG))
    parser.add_argument("--openmp-workers", type=int, default=4)
    parser.add_argument("--cuda-threads-per-block", type=int, default=256)
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--save-dir", default="reports")
    args = parser.parse_args()

    lines, io_time, total_bytes = read_lines_with_timing(args.input)
    openmp_result = benchmark_openmp(lines, workers=args.openmp_workers)
    cuda_result = benchmark_cuda(lines, threads_per_block=args.cuda_threads_per_block)

    rows: list[dict[str, float | int | str]] = [
        {
            "technology": "CPU OpenMP-like",
            "mode": f"{args.openmp_workers} workers",
            "time": float(openmp_result["time"]),
            "throughput_gb_s": float(openmp_result["throughput_gb_s"]),
            "tokens": int(openmp_result["tokens"]),
        },
        {
            "technology": "GPU CUDA",
            "mode": str(cuda_result["mode"]),
            "time": float(cuda_result["time"]),
            "throughput_gb_s": float(cuda_result["throughput_gb_s"]),
            "tokens": int(cuda_result["tokens"]),
        },
    ]
    top_rows = top_words(lines, top_n=args.top_n)

    out_dir = Path(args.save_dir)
    plots_dir = out_dir / "plots"
    pd.DataFrame(rows).to_csv(out_dir / "benchmark_cpu_gpu.csv", index=False)
    pd.DataFrame(top_rows, columns=["word", "count"]).to_csv(
        out_dir / "top_words.csv",
        index=False,
    )
    plot_cpu_gpu_comparison(rows, str(plots_dir / "cpu_gpu_throughput.png"))
    plot_top_words(top_rows, str(plots_dir / "top_words.png"))
    write_markdown_report(
        out_dir / "benchmark_report.md",
        rows,
        top_rows,
        io_time,
        total_bytes,
    )
    print(pd.DataFrame(rows))
    print(f"Saved report to: {out_dir / 'benchmark_report.md'}")


if __name__ == "__main__":
    main()

import time

from parallel.openmp.tokenizer import (
    count_tokens_parallel,
)
from parallel.openmp.reduction import (
    reduce_local_token_counters
)


def benchmark_openmp(
        lines: list[str],
        workers: int = 4,
        backend: str = "thread",
):

    start = time.perf_counter()
    total_bytes = len("".join(lines).encode("utf-8", errors="ignore"))

    local_counters = count_tokens_parallel(lines, workers=workers, backend=backend)
    merged_counter = reduce_local_token_counters(local_counters)

    end = time.perf_counter()
    elapsed = end - start

    return {
        "time": elapsed,
        "tokens": int(sum(merged_counter.values())),
        "bytes": total_bytes,
        "throughput_gb_s": (total_bytes / elapsed / 1_000_000_000) if elapsed > 0 else 0.0,
        "vocabulary_size": len(merged_counter),
        "workers": workers,
        "backend": backend,
        "local_dicts": len(local_counters),
        "global_token_total_from_reduction": int(sum(merged_counter.values())),
    }

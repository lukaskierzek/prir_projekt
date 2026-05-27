import time

from parallel.openmp.tokenizer import (
    tokenize_and_encode_parallel
)

from parallel.openmp.histogram import (
    build_histogram
)
from parallel.openmp.reduction import (
    reduce_local_token_counters
)


def benchmark_openmp(
        lines: list[str],
        workers: int = 4
):

    start = time.perf_counter()
    total_bytes = len("".join(lines).encode("utf-8", errors="ignore"))

    encoded, vocabulary, local_counters = (
        tokenize_and_encode_parallel(
            lines
            , workers=workers
        )
    )

    histogram = build_histogram(
        encoded,
        len(vocabulary)
    )
    merged_counter = reduce_local_token_counters(
        local_counters
    )

    end = time.perf_counter()
    elapsed = end - start

    return {
        "time": elapsed,
        "tokens": len(encoded),
        "bytes": total_bytes,
        "throughput_gb_s": (total_bytes / elapsed / 1_000_000_000) if elapsed > 0 else 0.0,
        "vocabulary_size": len(vocabulary),
        "workers": workers,
        "local_dicts": len(local_counters),
        "global_token_total_from_reduction": int(sum(merged_counter.values())),
        "global_token_total_from_histogram": int(histogram.sum())
    }

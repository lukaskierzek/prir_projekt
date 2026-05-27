from collections import Counter
from time import perf_counter

from parallel.mpi.chunking import split_lines_for_ranks
from parallel.mpi.reduction import merge_token_counters


def _token_counter(lines: list[str]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for line in lines:
        counter.update(line.upper().split())
    return counter


def run_mpi_token_count(lines: list[str]) -> dict[str, int | float]:
    """
    MPI-ready API. If started with `mpiexec`, uses mpi4py scatter/gather/reduce.
    Fallback: single-process execution (still keeps same result schema).
    """
    start = perf_counter()
    total_bytes = len("".join(lines).encode("utf-8", errors="ignore"))
    try:
        from mpi4py import MPI  # type: ignore
    except Exception:
        local_counter = _token_counter(lines)
        return {
            "world_size": 1,
            "rank": 0,
            "tokens": int(sum(local_counter.values())),
            "bytes": total_bytes,
            "vocabulary_size": len(local_counter),
            "time": perf_counter() - start,
            "throughput_gb_s": total_bytes / (perf_counter() - start) / 1_000_000_000,
            "mode": "single-process-fallback",
        }

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    world_size = comm.Get_size()

    chunks = split_lines_for_ranks(lines, world_size) if rank == 0 else None
    local_lines = comm.scatter(chunks, root=0)
    local_counter = _token_counter(local_lines)

    gathered = comm.gather(local_counter, root=0)
    if rank != 0:
        elapsed = perf_counter() - start
        return {
            "world_size": world_size,
            "rank": rank,
            "tokens": int(sum(local_counter.values())),
            "bytes": len("".join(local_lines).encode("utf-8", errors="ignore")),
            "vocabulary_size": len(local_counter),
            "time": elapsed,
            "throughput_gb_s": 0.0,
            "mode": "worker",
        }

    merged = merge_token_counters(gathered)
    elapsed = perf_counter() - start
    return {
        "world_size": world_size,
        "rank": 0,
        "tokens": int(sum(merged.values())),
        "bytes": total_bytes,
        "vocabulary_size": len(merged),
        "time": elapsed,
        "throughput_gb_s": (total_bytes / elapsed / 1_000_000_000) if elapsed > 0 else 0.0,
        "mode": "mpi-root",
    }

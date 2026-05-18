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
    try:
        from mpi4py import MPI  # type: ignore
    except Exception:
        local_counter = _token_counter(lines)
        return {
            "world_size": 1,
            "rank": 0,
            "tokens": int(sum(local_counter.values())),
            "vocabulary_size": len(local_counter),
            "time": perf_counter() - start,
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
        return {
            "world_size": world_size,
            "rank": rank,
            "tokens": int(sum(local_counter.values())),
            "vocabulary_size": len(local_counter),
            "time": perf_counter() - start,
            "mode": "worker",
        }

    merged = merge_token_counters(gathered)
    return {
        "world_size": world_size,
        "rank": 0,
        "tokens": int(sum(merged.values())),
        "vocabulary_size": len(merged),
        "time": perf_counter() - start,
        "mode": "mpi-root",
    }

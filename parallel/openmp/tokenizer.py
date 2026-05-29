from collections import Counter
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def _tokenize_chunk(
        chunk: list[str]
) -> Counter:
    local_counter = Counter()
    for line in chunk:
        local_counter.update(line.upper().split())
    return local_counter


def _split_chunks(
        lines: list[str],
        chunks: int
) -> list[list[str]]:
    if not lines:
        return []

    chunks = max(1, min(chunks, len(lines)))
    chunk_size = (len(lines) + chunks - 1) // chunks
    return [
        lines[i:i + chunk_size]
        for i in range(0, len(lines), chunk_size)
    ]


def tokenize_and_encode_parallel(
        lines: list[str],
        workers: int = 4,
        backend: str = "thread",
) -> tuple[list[int], dict[str, int], list[Counter]]:
    """
    Parallel tokenization flow:
    1) Parallel tokenization into local counters.
    2) Final reduction of local counters.
    3) Build global vocabulary and encoded stream.

    Returns:
        encoded words
        vocabulary mapping
        local counters (for reporting/debug)
    """
    if not lines:
        return [], {}, []

    chunks = _split_chunks(lines, workers)

    executor_cls = ProcessPoolExecutor if backend == "process" else ThreadPoolExecutor
    with executor_cls(max_workers=workers) as executor:
        local_counters = list(executor.map(_tokenize_chunk, chunks))

    global_counter = Counter()
    for counter in local_counters:
        global_counter.update(counter)

    vocabulary = {
        token: idx for idx, token in enumerate(sorted(global_counter.keys()))
    }

    encoded = []
    for line in lines:
        words = line.upper().split()
        for word in words:
            encoded.append(vocabulary[word])

    return encoded, vocabulary, local_counters


def count_tokens_parallel(
        lines: list[str],
        workers: int = 4,
        backend: str = "process",
) -> list[Counter]:
    """
    Count tokens in local per-worker dictionaries.

    Reduction is intentionally done by the caller so the benchmark can report
    the tokenization and merge phases separately.
    """
    if not lines:
        return []

    chunks = _split_chunks(lines, workers)
    executor_cls = ProcessPoolExecutor if backend == "process" else ThreadPoolExecutor
    with executor_cls(max_workers=workers) as executor:
        return list(executor.map(_tokenize_chunk, chunks))


def tokenize_and_encode(
        lines: list[str]
) -> tuple[list[int], dict[str, int]]:
    encoded, vocabulary, _ = tokenize_and_encode_parallel(
        lines,
        workers=1
    )
    return encoded, vocabulary

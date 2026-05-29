from __future__ import annotations

import time

import numpy as np


WHITESPACE_BYTES = frozenset({9, 10, 11, 12, 13, 32})


def _flatten_lines(lines: list[str]) -> np.ndarray:
    payload = "".join(lines).encode("utf-8", errors="ignore")
    return np.frombuffer(payload, dtype=np.uint8).copy()


def _count_tokens_cpu(data: np.ndarray) -> tuple[int, np.ndarray]:
    histogram = np.bincount(data, minlength=256).astype(np.int64)
    in_token = False
    tokens = 0

    for byte in data:
        is_space = int(byte) in WHITESPACE_BYTES
        if is_space:
            in_token = False
        elif not in_token:
            tokens += 1
            in_token = True

    return tokens, histogram


def _run_cpu_fallback(data: np.ndarray, reason: str) -> dict[str, int | float | str]:
    start = time.perf_counter()
    tokens, histogram = _count_tokens_cpu(data)
    elapsed = time.perf_counter() - start
    return {
        "time": elapsed,
        "tokens": int(tokens),
        "bytes": int(data.size),
        "throughput_gb_s": (data.size / elapsed / 1_000_000_000) if elapsed > 0 else 0.0,
        "nonzero_byte_bins": int(np.count_nonzero(histogram)),
        "mode": "cpu-fallback",
        "fallback_reason": reason,
    }


def benchmark_cuda(
    lines: list[str],
    threads_per_block: int = 256,
) -> dict[str, int | float | str]:
    """
    Count text tokens and byte frequencies with a CUDA kernel.

    Text is flattened to bytes so the kernel can count token starts and byte
    frequencies without Python string handling on the device.
    """
    if threads_per_block <= 0:
        raise ValueError("threads_per_block must be > 0")

    data = _flatten_lines(lines)
    if data.size == 0:
        return {
            "time": 0.0,
            "tokens": 0,
            "bytes": 0,
            "throughput_gb_s": 0.0,
            "nonzero_byte_bins": 0,
            "mode": "empty-input",
        }

    try:
        from numba import cuda
    except Exception as exc:
        return _run_cpu_fallback(data, f"numba.cuda import failed: {exc}")

    try:
        if not cuda.is_available():
            return _run_cpu_fallback(data, "CUDA device is not available")

        if _token_histogram_kernel is None:
            return _run_cpu_fallback(data, "CUDA kernel is not initialized")

        start = time.perf_counter()
        device_data = cuda.to_device(data)
        device_histogram = cuda.to_device(np.zeros(256, dtype=np.int64))
        device_token_counts = cuda.to_device(np.zeros(data.size, dtype=np.int32))

        blocks = (data.size + threads_per_block - 1) // threads_per_block
        _token_histogram_kernel[blocks, threads_per_block](
            device_data,
            device_histogram,
            device_token_counts,
        )
        cuda.synchronize()

        histogram = device_histogram.copy_to_host()
        token_counts = device_token_counts.copy_to_host()
        elapsed = time.perf_counter() - start
    except Exception as exc:
        return _run_cpu_fallback(data, f"CUDA execution failed: {exc}")

    return {
        "time": elapsed,
        "tokens": int(token_counts.sum()),
        "bytes": int(data.size),
        "throughput_gb_s": (data.size / elapsed / 1_000_000_000) if elapsed > 0 else 0.0,
        "nonzero_byte_bins": int(np.count_nonzero(histogram)),
        "threads_per_block": threads_per_block,
        "blocks": int(blocks),
        "mode": "cuda",
    }


try:
    from numba import cuda

    @cuda.jit
    def _token_histogram_kernel(data, histogram, token_counts):
        idx = cuda.grid(1)
        if idx >= data.size:
            return

        byte = data[idx]
        cuda.atomic.add(histogram, byte, 1)

        is_space = (
            byte == 9
            or byte == 10
            or byte == 11
            or byte == 12
            or byte == 13
            or byte == 32
        )
        if is_space:
            return

        if idx == 0:
            token_counts[idx] = 1
            return

        previous = data[idx - 1]
        previous_is_space = (
            previous == 9
            or previous == 10
            or previous == 11
            or previous == 12
            or previous == 13
            or previous == 32
        )
        if previous_is_space:
            token_counts[idx] = 1

except Exception:
    _token_histogram_kernel = None

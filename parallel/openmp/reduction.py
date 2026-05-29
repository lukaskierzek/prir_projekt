import numpy as np
from collections import Counter


def reduce_histograms(
        histograms: list[np.ndarray]
):
    """
    Merge local histograms.
    """

    result = np.zeros_like(
        histograms[0]
    )

    for histogram in histograms:

        result += histogram

    return result


def reduce_local_token_counters(
        local_counters: list[Counter]
) -> Counter:
    """
    Merge per-chunk token counters into one global counter.
    """
    merged = Counter()

    for counter in local_counters:
        merged.update(counter)

    return merged

from collections import Counter


def merge_token_counters(
    counters: list[Counter[str]],
) -> Counter[str]:
    merged: Counter[str] = Counter()
    for counter in counters:
        merged.update(counter)
    return merged

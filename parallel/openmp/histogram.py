import numpy as np

def build_histogram(
        encoded_words,
        vocabulary_size
):
    """
    Deterministic histogram from encoded token ids.
    """
    if vocabulary_size == 0:
        return np.zeros(0, dtype=np.int64)
    return np.bincount(encoded_words, minlength=vocabulary_size).astype(np.int64)

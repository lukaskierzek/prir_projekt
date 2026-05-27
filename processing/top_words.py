from collections import Counter
import re


TOKEN_PATTERN = re.compile(r"\b[\w.-]+\b", re.IGNORECASE)


def count_words(lines: list[str]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for line in lines:
        counter.update(token.upper() for token in TOKEN_PATTERN.findall(line))
    return counter


def top_words(lines: list[str], top_n: int = 20) -> list[tuple[str, int]]:
    if top_n <= 0:
        return []
    return count_words(lines).most_common(top_n)

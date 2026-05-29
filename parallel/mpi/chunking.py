from collections.abc import Iterable


def split_lines_for_ranks(
    lines: list[str],
    world_size: int,
) -> list[list[str]]:
    if world_size <= 0:
        raise ValueError("world_size must be > 0")
    if not lines:
        return [[] for _ in range(world_size)]

    chunk_size = (len(lines) + world_size - 1) // world_size
    chunks = [lines[i : i + chunk_size] for i in range(0, len(lines), chunk_size)]
    if len(chunks) < world_size:
        chunks.extend([[] for _ in range(world_size - len(chunks))])
    return chunks


def iter_file_chunks(
    file_path: str,
    chunk_lines: int,
) -> Iterable[list[str]]:
    if chunk_lines <= 0:
        raise ValueError("chunk_lines must be > 0")

    with open(file_path, "r", encoding="utf-8") as handle:
        chunk: list[str] = []
        for line in handle:
            chunk.append(line)
            if len(chunk) >= chunk_lines:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

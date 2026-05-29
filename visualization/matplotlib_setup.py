import os
from pathlib import Path


def configure_matplotlib(cache_dir: str | Path = ".matplotlib") -> None:
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("MPLCONFIGDIR", str(Path(cache_dir).resolve()))

import subprocess
import time

from contextlib import contextmanager


def run_command(command: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )

    print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return result


@contextmanager
def timer(name: str):
    print(f"Starting {name}...")
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    print(f"{name} took {end - start:.2f} seconds")

from config import DEFAULT_INPUT_LOG, OPENMP_WORKERS
from parallel.mpi.runner import run_mpi_token_count
from parallel.openmp.benchmark import benchmark_openmp


def load_lines(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as handle:
        return handle.readlines()


def run_openmp_experiment(lines: list[str]) -> dict:
    return benchmark_openmp(lines, workers=OPENMP_WORKERS)


def run_mpi_experiment(lines: list[str]) -> dict:
    return run_mpi_token_count(lines)


if __name__ == "__main__":
    data = load_lines(str(DEFAULT_INPUT_LOG))
    print("OpenMP-like:", run_openmp_experiment(data))
    print("MPI:", run_mpi_experiment(data))

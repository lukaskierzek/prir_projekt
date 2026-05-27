# Parallel Log Analysis (Python Only)

Zakres projektu:
- analiza logow i filtrowanie,
- OpenMP-like w Pythonie: rownolegla tokenizacja, lokalne slowniki/liczniki, koncowa redukcja,
- MPI (`mpi4py`): podzial danych miedzy procesy i laczenie wynikow,
- CUDA (`numba.cuda`): zliczanie tokenow i histogramu bajtow na GPU, z CPU fallbackiem gdy CUDA nie jest dostepna.

## Szybki start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Analiza bazowa

```bash
python main.py --input data/raw/Hadoop_2k.log
```

## OpenMP-like (Python threads)

```bash
python main.py --input data/raw/Hadoop_2k.log --parallel-mode openmp --openmp-workers 4
```

## MPI (fallback 1 proces)

```bash
python main.py --input data/raw/Hadoop_2k.log --parallel-mode mpi
```

## MPI (wiele procesow)

```bash
mpiexec -n 4 python main.py --input data/raw/Hadoop_2k.log --parallel-mode mpi
```

## CUDA

```bash
python main.py --input data/raw/Hadoop_2k.log --parallel-mode cuda --cuda-threads-per-block 256
```

Benchmark CUDA:

```bash
python cuda_speedup.py --input data/raw/Hadoop_200k.log --threads-per-block 64 128 256 512
```

## Wyniki do raportu

Ten skrypt generuje top-N slow, porownanie CPU/GPU, przepustowosc GB/s oraz krotki
wniosek o tym, czy I/O jest waskim gardlem:

```bash
python benchmark_report.py --input data/raw/Hadoop_200k.log --openmp-workers 4 --top-n 20
```

Wyniki:
- `reports/benchmark_cpu_gpu.csv`
- `reports/top_words.csv`
- `reports/benchmark_report.md`
- `reports/plots/cpu_gpu_throughput.png`
- `reports/plots/top_words.png`

## Wykresy przyspieszenia i efektywnosci

Notebook: `experiments.ipynb`  
OpenMP benchmark: `openmp_speedup.py`  
MPI benchmark: `mpi_speedup.py`  
CUDA benchmark: `cuda_speedup.py`  
Raport CPU/GPU + top-N: `benchmark_report.py`  
Porownanie najlepszych wynikow: `best_comparison.py`  
Alias deprecated: `experiments_openmp_mpi.py`

## Technologie

- Python 3.11
- numpy, pandas, matplotlib
- numba / numba.cuda
- mpi4py
- pytest

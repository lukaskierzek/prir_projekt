# Parallel Log Analysis (Python Only)

Aktualny zakres:
- analiza logów i filtrowanie,
- OpenMP-like w Pythonie: równoległa tokenizacja, lokalne słowniki/liczniki, końcowa redukcja,
- przygotowane podłoże pod MPI (`mpi4py`): podział danych między procesy i łączenie wyników.

## Szybki start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Uruchomienie analizy bazowej

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

## MPI (wiele procesów)

```bash
mpiexec -n 4 python main.py --input data/raw/Hadoop_2k.log --parallel-mode mpi
```

## Wykresy przyspieszenia i efektywności

Notebook: `experiments.ipynb` (dodane komórki benchmarkowe)  
Skrypt porównawczy: `best_comparison.py`  
Alias (deprecated): `experiments_openmp_mpi.py`

## Technologie

- Python 3.11
- numpy, pandas, matplotlib
- numba (OpenMP-like ścieżki obliczeń)
- mpi4py
- pytest


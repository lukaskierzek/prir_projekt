# Parallel Log Analysis

Projekt analizuje logi Hadoop i porównuje kilka wariantów przetwarzania:
wersję bazową, OpenMP-like w Pythonie, MPI oraz CUDA z fallbackiem CPU.
Kod jest podzielony na niezależne moduły, dzięki czemu ten sam pipeline można
uruchamiać z poziomu CLI, notebooków oraz skryptów benchmarkowych.

## Spis Treści

- [Zakres](#zakres)
- [Pipeline](#pipeline)
- [Struktura projektu](#struktura-projektu)
- [Wymagania](#wymagania)
- [Szybki start](#szybki-start)
- [Analiza bazowa](#analiza-bazowa)
- [OpenMP-like](#openmp-like)
- [MPI](#mpi)
- [CUDA](#cuda)
- [Wyniki do raportu](#wyniki-do-raportu)
- [Notebooki](#notebooki)
- [Dane](#dane)
- [Technologie](#technologie)

## Zakres

- parsowanie logów i filtrowanie po poziomie, frazie oraz zakresie dat,
- zliczanie poziomów logów i fraz w treści komunikatów,
- agregacja zdarzeń wybranego typu w przedziałach godzinowych,
- eksport wyników do JSON/CSV,
- benchmarki OpenMP-like, MPI i CUDA,
- wykresy do raportu: przyspieszenie, efektywność, przepustowość, top-N słów i wpływ I/O.

## Pipeline

Główny przepływ danych wygląda następująco:

```text
raw .log
  -> parser/log_parser.py
  -> AnalysisConfig
  -> processing/analyzer.py
  -> AnalysisResult
  -> report.py / visualization/
  -> reports/*.csv, reports/*.json, reports/plots/*.png
```

Warianty równoległe korzystają z tych samych danych wejściowych, ale mierzą inny
fragment pracy:

- OpenMP-like: równoległa tokenizacja, lokalne liczniki i redukcja.
- MPI: podział linii między procesy, lokalne zliczanie i scalenie na root.
- CUDA: spłaszczenie tekstu do bajtów, kernel GPU dla tokenów i histogramu bajtów.

## Struktura projektu

- `main.py` - główny interfejs CLI do analizy logów.
- `parser/` - parser linii logów.
- `processing/` - filtrowanie, analiza, statystyki i top-N słów.
- `parallel/openmp/` - równoległa tokenizacja, lokalne liczniki i redukcja.
- `parallel/mpi/` - podział danych między procesy MPI i scalanie wyników.
- `parallel/cuda/` - zliczanie tokenów i histogramu bajtów na GPU lub CPU fallback.
- `visualization/` - funkcje generujące wykresy.
- `reports/` - wygenerowane raporty, CSV i wykresy.
- `tests/` - testy jednostkowe.
- `experiments.ipynb` - notebook eksperymentalny.
- `pipeline_presentation.ipynb` - notebook prezentacyjny z pełnym pipeline.

## Wymagania

- Python 3.11+
- pakiety z `requirements.txt`
- opcjonalnie `mpiexec` do uruchomień MPI z wieloma procesami
- opcjonalnie karta NVIDIA/CUDA dla rzeczywistego trybu GPU

Jeśli MPI lub CUDA nie są dostępne, projekt nadal działa:
- MPI uruchamia wariant jednego procesu,
- CUDA przechodzi w kontrolowany `cpu-fallback`.

## Szybki start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Uruchom testy:

```bash
python -m pytest -q
```

## Analiza bazowa

```bash
python main.py --input data/raw/Hadoop_2k.log
```

Przykład z filtrami:

```bash
python main.py --input data/raw/Hadoop_2k.log --level ERROR --phrase timeout --limit 10
```

Przykład z zakresem dat:

```bash
python main.py --input data/raw/Hadoop_2k.log --from-date 2015-10-18 --to-date 2015-10-18
```

Eksport wyników:

```bash
python main.py --input data/raw/Hadoop_2k.log --output-json reports/report.json --output-filtered-csv reports/filtered.csv
```

## OpenMP-like

Wariant OpenMP-like używa równoległej tokenizacji w Pythonie, lokalnych słowników/liczników i końcowej redukcji.
Wyniki należy interpretować razem z rozmiarem danych: dla małych plików narzut
uruchamiania workerów może być większy niż zysk z równoległości.

```bash
python main.py --input data/raw/Hadoop_2k.log --parallel-mode openmp --openmp-workers 4
```

Benchmark przyspieszenia:

```bash
python openmp_speedup.py --input data/raw/Hadoop_200k.log --threads 1 2 4 8
```

## MPI

Fallback jednego procesu:

```bash
python main.py --input data/raw/Hadoop_2k.log --parallel-mode mpi
```

Uruchomienie z wieloma procesami:

```bash
mpiexec -n 4 python main.py --input data/raw/Hadoop_2k.log --parallel-mode mpi
```

Benchmark przyspieszenia:

```bash
python mpi_speedup.py --input data/raw/Hadoop_200k.log --procs 1 2 4 8
```

## CUDA

Tryb CUDA używa `numba.cuda`. Jeśli CUDA nie jest dostępna, kod zwraca wynik
w trybie `cpu-fallback`, zamiast przerywać działanie projektu.

```bash
python main.py --input data/raw/Hadoop_2k.log --parallel-mode cuda --cuda-threads-per-block 256
```

Benchmark CUDA:

```bash
python cuda_speedup.py --input data/raw/Hadoop_200k.log --threads-per-block 64 128 256 512
```

## Wyniki do raportu

Skrypt `benchmark_report.py` generuje top-N słów, porównanie CPU/GPU,
przepustowość GB/s oraz krótki wniosek o tym, czy I/O jest wąskim gardłem:

```bash
python benchmark_report.py --input data/raw/Hadoop_200k.log --openmp-workers 4 --top-n 20
```

Główne artefakty:

- `reports/benchmark_cpu_gpu.csv`
- `reports/top_words.csv`
- `reports/benchmark_report.md`
- `reports/plots/cpu_gpu_throughput.png`
- `reports/plots/top_words.png`

Dodatkowe wykresy:

```bash
python extra_visualizations.py --input data/raw/Hadoop_200k.log
```

Wyniki:

- `reports/plots/level_counts.png`
- `reports/plots/top_error_hours.png`
- `reports/plots/io_vs_compute_time.png`
- `reports/plots/openmp_mpi_speedup.png`

Porównanie najlepszych czasów OpenMP-like, MPI i CUDA:

```bash
python best_comparison.py --input data/raw/Hadoop_200k.log
```

Typowy zestaw komend do odświeżenia raportu:

```bash
python openmp_speedup.py --input data/raw/Hadoop_200k.log --threads 1 2 4 8
python mpi_speedup.py --input data/raw/Hadoop_200k.log --procs 1 2 4 8
python cuda_speedup.py --input data/raw/Hadoop_200k.log --threads-per-block 64 128 256 512
python benchmark_report.py --input data/raw/Hadoop_200k.log --openmp-workers 4 --top-n 20
python extra_visualizations.py --input data/raw/Hadoop_200k.log
python best_comparison.py --input data/raw/Hadoop_200k.log
```

## Notebooki

- `experiments.ipynb` - krótszy notebook do eksperymentów i szybkiego sprawdzenia pipeline.
- `pipeline_presentation.ipynb` - notebook prezentacyjny prowadzący przez parsing, CLI, statystyki, eksport, wizualizację i benchmarki.

Notebooki korzystają ze ścieżek z `config.py`, dlatego powinny działać po uruchomieniu z katalogu głównego projektu.
Zapisane wyniki w notebookach pełnią rolę referencyjnego przebiegu eksperymentu.

## Dane

Domyślne pliki wejściowe:

- `data/raw/Hadoop_2k.log` - mały plik do szybkich testów i demonstracji,
- `data/raw/Hadoop_200k.log` - większy plik do benchmarków.

## Technologie

- Python
- numpy
- pandas
- matplotlib
- numba / numba.cuda
- mpi4py
- pytest
